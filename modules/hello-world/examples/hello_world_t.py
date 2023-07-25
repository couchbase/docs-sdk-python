from datetime import timedelta

# needed for any cluster connection
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
# needed for options -- cluster, timeout, SQL++ (N1QL) query, etc.
from couchbase.options import (ClusterOptions, ClusterTimeoutOptions,
                               QueryOptions)

# tag::connect[]
# Update this to your cluster
username = "Administrator"
password = "password"
bucket_name = "travel-sample"
# User Input ends here.

# Connect options - authentication
auth = PasswordAuthenticator(
    username,
    password,
)

# Get a reference to our cluster
# NOTE: For TLS/SSL connection use 'couchbases://<your-ip-address>' instead
cluster = Cluster('couchbase://your-ip', ClusterOptions(auth))

# Wait until the cluster is ready for use.
cluster.wait_until_ready(timedelta(seconds=5))
# end::connect[]

# tag::bucket[]
# get a reference to our bucket
cb = cluster.bucket(bucket_name)
# end::bucket[]

# tag::collection[]
cb_coll = cb.scope("inventory").collection("airline")
# end::collection[]

# tag::default-collection[]
# Get a reference to the default collection, required for older Couchbase server versions
cb_coll_default = cb.default_collection()
# end::default-collection[]

# tag::upsert-func[]
# upsert document function


def upsert_document(doc):
    print("\nUpsert CAS: ")
    try:
        # key will equal: "airline_8091"
        key = doc["type"] + "_" + str(doc["id"])
        result = cb_coll.upsert(key, doc)
        print(result.cas)
    except Exception as e:
        print(e)
# end::upsert-func[]

# tag::get-func[]
# get document function


def get_airline_by_key(key):
    print("\nGet Result: ")
    try:
        result = cb_coll.get(key)
        print(result.content_as[str])
    except Exception as e:
        print(e)
# end::get-func[]

# tag::lookup-func[]
# query for new document by callsign


def lookup_by_callsign(cs):
    print("\nLookup Result: ")
    try:
        inventory_scope = cb.scope('inventory')
        sql_query = 'SELECT VALUE name FROM airline WHERE callsign = $1'
        row_iter = inventory_scope.query(
            sql_query,
            QueryOptions(positional_parameters=[cs]))
        for row in row_iter:
            print(row)
    except Exception as e:
        print(e)
# end::lookup-func[]


# tag::test-doc[]
airline = {
    "type": "airline",
    "id": 8091,
    "callsign": "CBS",
    "iata": None,
    "icao": None,
    "name": "Couchbase Airways",
}
# end::test-doc[]

# tag::upsert-invoke[]
upsert_document(airline)
# end::upsert-invoke[]

# tag::get-invoke[]
get_airline_by_key("airline_8091")
# end::get-invoke[]

# tag::lookup-invoke[]
lookup_by_callsign("CBS")
# end::lookup-invoke[]
