from datetime import timedelta

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.exceptions import QueryIndexAlreadyExistsException
from couchbase.management.options import (BuildDeferredQueryIndexOptions,
                                          CreatePrimaryQueryIndexOptions,
                                          CreateQueryIndexOptions,
                                          WatchQueryIndexOptions)
from couchbase.options import ClusterOptions


def primary_index(query_index_mgr):
    print("Example - [primary]")
    # tag::primary[]
    query_index_mgr.create_primary_index(CreatePrimaryQueryIndexOptions(
        # Set this if you wish to use a custom name
        # index_name="custom_name",
        ignore_if_exists=True
    ))
    # end::primary[]


def secondary_index(query_index_mgr):
    print("Example - [secondary]")
    # tag::secondary[]
    try:
        query_index_mgr.create_index("tenant_agent_01_users_email", ["preferred_email"])
    except QueryIndexAlreadyExistsException:
        print("Index already exists")
    # end::secondary[]


def defer_and_watch_index(query_index_mgr):
    print("Example - [defer-indexes]")
    # tag::defer-indexes[]
    try:
        # Create a deferred index
        query_index_mgr.create_index("tenant_agent_01_users_phone", ["preferred_phone"],
                                     CreateQueryIndexOptions(deferred=True))

        # Build any deferred indexes within `travel-sample`.tenant_agent_01.users
        query_index_mgr.build_deferred_indexes(BuildDeferredQueryIndexOptions())

        # Wait for indexes to come online
        query_index_mgr.watch_indexes(["tenant_agent_01_users_phone"],
                                      WatchQueryIndexOptions(timeout=timedelta(seconds=30)))
    except QueryIndexAlreadyExistsException:
        print("Index already exists")
    # end::defer-indexes[]


def drop_primary_and_secondary_index(query_index_mgr):
    print("Example - [drop-primary-or-secondary-index]")
    # tag::drop-primary-or-secondary-index[]
    # Drop a primary index
    query_index_mgr.drop_primary_index()

    # Drop a secondary index
    query_index_mgr.drop_index("tenant_agent_01_users_email")
    # end::drop-primary-or-secondary-index[]


# tag::creating-index-mgr[]
cluster = Cluster(
    "couchbase://your-ip",
    ClusterOptions(PasswordAuthenticator("Administrator", "password"))
)

collection = cluster.bucket("travel-sample").scope("tenant_agent_01").collection("users")
query_index_mgr = collection.query_indexes()
# end::creating-index-mgr[]

primary_index(query_index_mgr)
secondary_index(query_index_mgr)
defer_and_watch_index(query_index_mgr)
drop_primary_and_secondary_index(query_index_mgr)
