# tag::simple_query[]
from acouchbase.cluster import Cluster, get_event_loop
from couchbase.options import ClusterOptions, QueryOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import ParsingFailedException


async def get_couchbase():
    cluster = Cluster(
        "couchbase://your-ip",
        ClusterOptions(PasswordAuthenticator("Administrator", "password")))
    bucket = cluster.bucket("travel-sample")
    await bucket.on_connect()
    collection = bucket.default_collection()

    return cluster, bucket, collection


async def simple_query(cluster):
    try:
        result = cluster.query(
            "SELECT ts.* FROM `travel-sample` ts WHERE ts.`type`=$type LIMIT 10",
            QueryOptions(named_parameters={"type": "hotel"}))
        async for row in result:
            print("Found row: {}".format(row))
    except ParsingFailedException as ex:
        print(ex)

loop = get_event_loop()
cluster, bucket, collection = loop.run_until_complete(get_couchbase())
loop.run_until_complete(simple_query(cluster))
# end::simple_query[]
