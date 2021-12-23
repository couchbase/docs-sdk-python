
import traceback
import functools
import time
from typing import Optional, Tuple, Callable
import warnings


from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.collection import InsertOptions, ReplaceOptions
from couchbase.exceptions import (CASMismatchException, CouchbaseException,
                                  CouchbaseTransientException, DocumentNotFoundException,
                                  DocumentExistsException,
                                  DurabilitySyncWriteAmbiguousException, QueryErrorContext)
from couchbase.durability import Durability, ServerDurability

# ErrorContext is still uncommited in the Python SDK, ignore the runtime warnings for the example
warnings.filterwarnings("ignore")

cluster = Cluster(
    "couchbase://172.23.111.131",
    authenticator=PasswordAuthenticator(
        "Administrator",
        "password"))
bucket = cluster.bucket("travel-sample")
collection = bucket.scope("inventory").collection("hotel")

# tag::generic_try_catch[]
try:
    res = collection.get("not-a-key")
except CouchbaseException:
    # we can handle any exceptions thrown here.
    pass
# end::generic_try_catch[]


# tag::retries[]
def allow_retries(retry_limit=3,                # type: int
                  backoff=1.0,                  # type: float
                  exponential_backoff=False,    # type: bool
                  linear_backoff=False,         # type: bool
                  allowed_exceptions=None       # type: Optional[Tuple]
                  ) -> Callable:
    def handle_retries(func):
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            for i in range(retry_limit):
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    if allowed_exceptions is None or not isinstance(ex, allowed_exceptions):
                        raise

                    if (retry_limit-1)-i == 0:
                        raise

                    delay = backoff
                    if exponential_backoff is True:
                        delay *= (2**i)
                    elif linear_backoff is True:
                        delay *= (i+1)

                    print(f"Retries left: {(retry_limit-1) - i}")
                    print(f"Backing Off: {delay} seconds")
                    time.sleep(delay)

        return func_wrapper
    return handle_retries


@allow_retries(retry_limit=5,
               backoff=0.5,
               allowed_exceptions=(CASMismatchException, CouchbaseTransientException))
def update_with_cas(collection,    # type: str
                    doc_key       # type: str
                    ) -> bool:

    result = collection.get(doc_key)
    content = result.content_as[dict]
    reviews = content.get("reviews", 0)
    content["total_reviews"] = reviews if reviews == 0 else len(reviews)
    collection.replace(doc_key, content, ReplaceOptions(cas=result.cas))


key = "hotel_10026"
update_with_cas(collection, key)
# end::retries[]

# tag::DocumentNotFoundException[]
try:
    key = "not-a-key"
    res = collection.get(key)
except DocumentNotFoundException:
    print("doc with key: {} does not exist".format(key))
# end::DocumentNotFoundException[]

# tag::DocumentExistsException[]
try:
    key = "hotel_10026"
    res = collection.insert(
        key, {"title": "New Hotel", "name": "The New Hotel"})
except DocumentExistsException:
    print("doc with key: {} already exists".format(key))
# end::DocumentExistsException[]

# tag::CASMismatchException[]
try:
    result = collection.get("hotel_10026")
    collection.replace("hotel_10026", {}, cas=result.cas)
except CASMismatchException:
    # the CAS value has changed
    pass
# end::CASMismatchException[]

# tag::DurabilitySyncWriteAmbiguousException[]
for i in range(5):
    try:
        durability = ServerDurability(level=Durability.PERSIST_TO_MAJORITY)
        collection.insert(
            "my-key", {"title": "New Hotel"}, InsertOptions(durability=durability))
    except (DocumentExistsException, DurabilitySyncWriteAmbiguousException,) as ex:
        # if previously retried and the document now exists,
        # we can assume it was written successfully by a previous ambiguous exception
        if isinstance(ex, DocumentExistsException) and i > 0:
            continue

        # simply retry the durable operation again
        if isinstance(ex, DurabilitySyncWriteAmbiguousException):
            continue

        # raise the exception if not DocumentExistsException, DurabilitySyncWriteAmbiguousException
        raise
# end::DurabilitySyncWriteAmbiguousException[]

# tag::QueryErrorContext[]
try:
    cluster.query("SELECT * FROM default").rows()
except CouchbaseException as ex:
    if isinstance(ex.context, QueryErrorContext):
        # We have a N1QL error context, we can print out some useful information:
        print(ex.context.statement)
        print(ex.context.first_error_code)
        print(ex.context.first_error_message)
        print(ex.context.client_context_id)
        print(ex.context.endpoint)

# end::QueryErrorContext[]

try:
    collection.remove("my-key")
except CouchbaseException:
    pass
