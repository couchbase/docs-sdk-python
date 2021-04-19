import time

from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import (
    CollectionAlreadyExistsException,
    CollectionNotFoundException,
    ScopeAlreadyExistsException,
    ScopeNotFoundException)
from couchbase.management.collections import CollectionSpec


def retry(func, *args, back_off=0.5, limit=5, **kwargs):
    for i in range(limit):
        try:
            return func(*args, **kwargs)
        except Exception:
            print("Retry in {} seconds...".format((i + 1) * back_off))
            time.sleep((i + 1) * back_off)

    raise Exception(
        "Unable to successfully receive result from {}".format(func))


def get_scope(collection_mgr, scope_name):
    collection_mgr = bucket.collections()
    return next((s for s in collection_mgr.get_all_scopes()
                if s.name == scope_name), None)


def get_collection(collection_mgr, scope_name, coll_name):
    scope = get_scope(collection_mgr, scope_name)
    if scope:
        return next(
            (c for c in scope.collections if c.name == coll_name),
            None)

    return None

# tag::create_collections_mgr[]
cluster = Cluster(
    "couchbase://localhost",
    authenticator=PasswordAuthenticator(
        "Administrator",
        "password"))

bucket = cluster.bucket("default")
coll_manager = bucket.collections()
# end::create_collections_mgr[]

# tag::create_scope[]
try:
    coll_manager.create_scope("example-scope")
except ScopeAlreadyExistsException as ex:
    print(ex)
# end::create_scope[]

scope = retry(get_scope, coll_manager, "example-scope")
print("Found scope: {}".format(scope.name))

# tag::create_collection[]
collection_spec = CollectionSpec(
    "example-collection",
    scope_name="example-scope")

try:
    collection = coll_manager.create_collection(collection_spec)
except CollectionAlreadyExistsException as ex:
    print(ex)
# end::create_collection[]

collection = retry(
    get_collection,
    coll_manager,
    "example-scope",
    "example-collection")
print("Found collection: {}".format(collection.name))

# tag::drop_collection[]
try:
    coll_manager.drop_collection(collection_spec)
except CollectionNotFoundException as ex:
    print(ex)
# end::drop_collection[]

# tag::drop_scope[]
try:
    coll_manager.drop_scope("example-scope")
except ScopeNotFoundException as ex:
    print(ex)
# end::drop_scope[]

