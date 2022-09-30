# tag::simple_query[]
from acouchbase.cluster import Cluster, get_event_loop
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
import couchbase.search as search


async def get_couchbase():
    cluster = Cluster(
        "couchbase://localhost",
        ClusterOptions(PasswordAuthenticator("Administrator", "password")))
    bucket = cluster.bucket("travel-sample")
    await bucket.on_connect()
    collection = bucket.default_collection()

    return cluster, bucket, collection

# NOTE: the travel-sample-index search index might need to be created
async def simple_query(cluster):
    try:
        result = cluster.search_query(
            "travel-sample-index", search.QueryStringQuery("swanky"))

        async for row in result:
            print("Found row: {}".format(row))
        
    except CouchbaseException as ex:
        print(ex)


loop = get_event_loop()
cluster, bucket, collection = loop.run_until_complete(get_couchbase())
loop.run_until_complete(simple_query(cluster))

# end::simple_query[]
