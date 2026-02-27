from datetime import timedelta

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.exceptions import QueryIndexAlreadyExistsException
from couchbase.management.queries import (BuildDeferredQueryIndexOptions,
                                          CreatePrimaryQueryIndexOptions,
                                          CreateQueryIndexOptions,
                                          DropPrimaryQueryIndexOptions,
                                          DropQueryIndexOptions,
                                          WatchQueryIndexOptions)


def primary_index(query_index_mgr):
    print("Example - [primary]")
    # tag::primary[]
    query_index_mgr.create_primary_index("travel-sample", CreatePrimaryQueryIndexOptions(
        scope_name="tenant_agent_01",
        collection_name="users",
        # Set this if you wish to use a custom name
        # index_name="custom_name",
        ignore_if_exists=True
    ))
    # end::primary[]


def secondary_index(query_index_mgr):
    print("Example - [secondary]")
    # tag::secondary[]
    try:
        query_index_mgr.create_index("travel-sample", "tenant_agent_01_users_email", ["preferred_email"], CreateQueryIndexOptions(
            scope_name="tenant_agent_01",
            collection_name="users"
        ))
    except QueryIndexAlreadyExistsException:
        print("Index already exists")
    # end::secondary[]


def defer_and_watch_index(query_index_mgr):
    print("Example - [defer-indexes]")
    # tag::defer-indexes[]
    try:
        # Create a deferred index
        query_index_mgr.create_index("travel-sample", "tenant_agent_01_users_phone", ["preferred_phone"], CreateQueryIndexOptions(
            scope_name="tenant_agent_01",
            collection_name="users",
            deferred=True
        ))

        # Build any deferred indexes within `travel-sample`.tenant_agent_01.users
        query_index_mgr.build_deferred_indexes("travel-sample", BuildDeferredQueryIndexOptions(
            scope_name="tenant_agent_01",
            collection_name="users"
        ))

        # Wait for indexes to come online
        query_index_mgr.watch_indexes("travel-sample", ["tenant_agent_01_users_phone"], WatchQueryIndexOptions(
            scope_name="tenant_agent_01",
            collection_name="users",
            timeout=timedelta(seconds=30)
        ))
    except QueryIndexAlreadyExistsException:
        print("Index already exists")
    # end::defer-indexes[]


def drop_primary_and_secondary_index(query_index_mgr):
    print("Example - [drop-primary-or-secondary-index]")
    # tag::drop-primary-or-secondary-index[]
    # Drop a primary index
    query_index_mgr.drop_primary_index("travel-sample", DropPrimaryQueryIndexOptions(
        scope_name="tenant_agent_01",
        collection_name="users"
    ))

    # Drop a secondary index
    query_index_mgr.drop_index("travel-sample", "tenant_agent_01_users_email", DropQueryIndexOptions(
        scope_name="tenant_agent_01",
        collection_name="users"
    ))
    # end::drop-primary-or-secondary-index[]


# tag::creating-index-mgr[]
cluster = Cluster(
    "couchbase://your-ip",
    authenticator=PasswordAuthenticator("Administrator", "password")
)

query_index_mgr = cluster.query_indexes()
# end::creating-index-mgr[]

primary_index(query_index_mgr)
secondary_index(query_index_mgr)
defer_and_watch_index(query_index_mgr)
drop_primary_and_secondary_index(query_index_mgr)
