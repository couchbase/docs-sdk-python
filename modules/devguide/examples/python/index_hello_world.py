from datetime import timedelta

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.management.queries import (CreatePrimaryQueryIndexOptions,
                                          CreateQueryIndexOptions,
                                          DropPrimaryQueryIndexOptions,
                                          WatchQueryIndexOptions)

cluster = Cluster('couchbase://localhost', ClusterOptions(
    PasswordAuthenticator('Administrator', 'password'))
)

print("[primary]")
# tag::primary[]
cluster.query_indexes().create_primary_index(
    "travel-sample",
    # Don't error if the primary index already exists.
    CreatePrimaryQueryIndexOptions(ignore_if_exists=True)
)
# end::primary[]
print("Index creation complete")

print("\n[named-primary]")
# tag::named-primary[]
cluster.query_indexes().create_primary_index(
    "travel-sample",
    CreatePrimaryQueryIndexOptions(index_name="named_primary_index")
)
# end::named-primary[]
print("Named primary index creation complete")

print("\n[secondary]")
# tag::secondary[]
cluster.query_indexes().create_index("travel-sample", "index_name", ["name"])
# end::secondary[]
print("Index creation complete")

print("\n[composite]")
# tag::composite[]
cluster.query_indexes().create_index(
    "travel-sample",
    "index_travel_info",
    ["name", "id", "icao", "iata"]
)
# end::composite[]
print("Index creation complete")

print("\n[drop-primary]")
# tag::drop-primary[]
cluster.query_indexes().drop_primary_index(
    "travel-sample"
)
# end::drop-primary[]
print("Primary index deleted successfully")

print("\n[drop-named-primary]")
# tag::drop-named-primary[]
cluster.query_indexes().drop_primary_index(
    "travel-sample",
    DropPrimaryQueryIndexOptions(index_name="named_primary_index")
)
# end::drop-named-primary[]
print("Named primary index deleted successfully")

print("\n[drop-secondary]")
# tag::drop-secondary[]
cluster.query_indexes().drop_index("travel-sample", "index_name")
# end::drop-secondary[]
print("Index deleted successfully")

print("\n[defer-create]")
# tag::defer-create-primary[]
cluster.query_indexes().create_primary_index(
    "travel-sample",
    CreatePrimaryQueryIndexOptions(deferred=True)
)
# end::defer-create-primary[]

# tag::defer-create-secondary[]
cluster.query_indexes().create_index(
    "travel-sample",
    "idx_name_email",
    ["name", "email"],
    CreateQueryIndexOptions(deferred=True)
)
# end::defer-create-secondary[]
print("Created deferred indexes")


print("\n[defer-build]")
# tag::defer-build[]
# Start building any deferred indexes which were previously created.
cluster.query_indexes().build_deferred_indexes("travel-sample")

# Wait for the deferred indexes to be ready for use.
# Set the maximum time to wait to 3 minutes.
cluster.query_indexes().watch_indexes(
    "travel-sample",
    ["idx_name_email"],
    WatchQueryIndexOptions(timeout=timedelta(minutes=3), watch_primary=True)
)
# end::defer-build[]
print("Deferred indexes ready")
