from datetime import timedelta

from couchbase.durability import (Durability, ServerDurability,
                                  ClientDurability, ReplicateTo, PersistTo)
from couchbase.exceptions import CouchbaseException, CASMismatchException
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.collection import (
    InsertOptions,
    ReplaceOptions,
    UpsertOptions,
    GetOptions,
    RemoveOptions,
    IncrementOptions,
    DecrementOptions)
from couchbase.collection import DeltaValue, SignedInt64

cluster = Cluster(
    "couchbase://your-ip",
    authenticator=PasswordAuthenticator(
        "Administrator",
        "password"))
bucket = cluster.bucket("travel-sample")
collection = bucket.default_collection()

# setup
try:
    # tag::remove[]
    result = collection.remove("document-key")
    # end::remove[]
    result = collection.remove("document-key-opts")
except CouchbaseException as ex:
    pass # may not exist in this example


# tag::insert[]
# Insert document
document = {"foo": "bar", "bar": "foo"}
result = collection.insert("document-key", document)
cas = result.cas
# end::insert[]

# tag::replace_cas[]
# Replace document with CAS
document = {"foo": "bar", "bar": "foo"}
result = collection.replace(
    "document-key",
    document,
    cas=cas,
    timeout=timedelta(
        minutes=1))
# end::replace_cas[]

try:
    # tag::get_cas_replace[]
    # Replace document with CAS
    result = collection.get("document-key")
    doc = result.content_as[dict]
    doc["bar"] = "baz"
    opts = ReplaceOptions(cas=result.cas)
    result = collection.replace("document-key", doc, opts)
    # end::get_cas_replace[]
except CASMismatchException as ex:
    print(ex)


# tag::insert_w_opts[]
# Insert document with options
document = {"foo": "bar", "bar": "foo"}
opts = InsertOptions(timeout=timedelta(seconds=5))
result = collection.insert("document-key-opts",
                           document,
                           opts,
                           expiry=timedelta(seconds=30))
# end::insert_w_opts[]


try:
    # tag::durability[]
    # Upsert with Durability (Couchbase Server >= 6.5) level Majority
    document = dict(foo="bar", bar="foo")
    opts = UpsertOptions(durability=ServerDurability(Durability.MAJORITY))
    result = collection.upsert("document-key", document, opts)
    # end::durability[]
except CouchbaseException as ex:
    # we expect an exception on local/test host, as Durability requirement
    # requires appropriately configured cluster
    pass

try:
    # tag::obs_durability[]
    # Upsert with observe based durability (Couchbase Server < 6.5)
    document = {"foo": "bar", "bar": "foo"}
    opts = UpsertOptions(
        durability=ClientDurability(
            ReplicateTo.ONE,
            PersistTo.ONE))
    result = collection.upsert("document-key", document, opts)
    # end::obs_durability[]
except CouchbaseException as ex:
    # we expect an exception on local/test host, as Durability requirement
    # requires appropriately configured cluster
    pass

# tag::get[]
result = collection.get("document-key")
print(result.content_as[dict])
# end::get[]

# tag::get_timeout[]
opts = GetOptions(timeout=timedelta(seconds=5))
result = collection.get("document-key", opts)
print(result.content_as[dict])
# end::get_timeout[]

try:
    # tag::remove_durability[]
    # remove document with options
    result = collection.remove(
        "document-key",
        RemoveOptions(
            cas=12345,
            durability=ServerDurability(
                Durability.MAJORITY)))
    # end::remove_durability[]
except CouchbaseException as ex:
    # we expect an exception here as the CAS value is chosen
    # for example purposes
    pass

# tag::touch[]
result = collection.touch("document-key", timedelta(seconds=10))
# end::touch[]

# tag::get_expiry[]
result = collection.get("document-key", GetOptions(with_expiry=True))
print("Expiry of result: {}".format(result.expiryTime))
# end::get_expiry[]

# tag::get_and_touch[]
result = collection.get_and_touch("document-key", timedelta(seconds=10))
# end::get_and_touch[]

# tag::increment[]
# Increment binary value by 1
collection.binary().increment(
    "counter-key",
    IncrementOptions(
        delta=DeltaValue(1)))
# end::increment[]

# tag::increment_w_seed[]
# Increment binary value by 5, if key doesn't exist, seed it at 1000
collection.binary().increment(
    "counter-key",
    IncrementOptions(
        delta=DeltaValue(5),
        initial=SignedInt64(1000)))
# end::increment_w_seed[]

# tag::decrement[]
# Decrement binary value by 1
collection.binary().decrement(
    "counter-key",
    DecrementOptions(
        delta=DeltaValue(1)))
# end::decrement[]

# tag::decrement_w_seed[]
# Decrement binary value by 2, if key doesn't exist, seed it at 1000
collection.binary().decrement(
    "counter-key",
    DecrementOptions(
        delta=DeltaValue(2),
        initial=SignedInt64(1000)))
# end::decrement_w_seed[]

print("Example: [named-collection-upsert]");
# tag::named-collection-upsert[]
agent_scope = bucket.scope("tenant_agent_00");
users_collection = agent_scope.collection("users");

content = {"name": "John Doe", "preferred_email": "johndoe111@test123.test" }

result = users_collection.upsert("user-key", content);
# end::named-collection-upsert[]