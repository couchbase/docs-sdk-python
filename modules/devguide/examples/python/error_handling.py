
import functools
import time
from typing import Callable, Optional, Tuple

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.durability import DurabilityLevel, ServerDurability
from couchbase.exceptions import (CASMismatchException,
                                  CouchbaseException,
                                  DocumentExistsException,
                                  DocumentNotFoundException,
                                  DurabilitySyncWriteAmbiguousException,
                                  QueryErrorContext)
from couchbase.options import ClusterOptions, InsertOptions, ReplaceOptions

cluster = Cluster.connect(
    "couchbase://your-ip",
    ClusterOptions(PasswordAuthenticator("Administrator", "password")))
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
            for attempt in range(retry_limit):
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    if allowed_exceptions is None or not isinstance(ex, allowed_exceptions):
                        raise

                    retries_left = retry_limit - attempt - 1
                    if retries_left == 0:
                        raise

                    delay = backoff
                    if exponential_backoff is True:
                        delay *= (2**attempt)
                    elif linear_backoff is True:
                        delay *= (attempt + 1)

                    print(f"Retries left: {retries_left}")
                    print(f"Backing Off: {delay} seconds")
                    time.sleep(delay)

        return func_wrapper
    return handle_retries


@allow_retries(retry_limit=5,
               backoff=0.5,
               allowed_exceptions=(CASMismatchException,))
def update_with_cas(collection,    # type: Collection
                    doc_key       # type: str
                    ) -> None:

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
    collection.replace("hotel_10026", {}, ReplaceOptions(cas=result.cas))
except CASMismatchException:
    # the CAS value has changed
    pass
# end::CASMismatchException[]

# tag::DurabilitySyncWriteAmbiguousException[]
durability = ServerDurability(level=DurabilityLevel.PERSIST_TO_MAJORITY)
for i in range(5):
    try:
        collection.insert(
            "my-key", {"title": "New Hotel"}, InsertOptions(durability=durability))
        break
    except DurabilitySyncWriteAmbiguousException:
        # the insert may or may not have been applied, so retry it
        continue
    except DocumentExistsException:
        # if we are retrying and the document now exists, a previous
        # ambiguous attempt was written successfully
        if i > 0:
            break
        raise
# end::DurabilitySyncWriteAmbiguousException[]

# tag::QueryErrorContext[]
try:
    cluster.query("SELECT * FROM no_such_bucket").execute()
except CouchbaseException as ex:
    if isinstance(ex.error_context, QueryErrorContext):
        # We have a Query error context, we can print out some useful information:
        print(ex.error_context.statement)
        print(ex.error_context.first_error_code)
        print(ex.error_context.first_error_message)
        print(ex.error_context.client_context_id)
        print(ex.error_context.last_dispatched_to)

# end::QueryErrorContext[]

print("DONE, tidying up")
try:
    collection.remove("my-key")
except CouchbaseException:
    pass
