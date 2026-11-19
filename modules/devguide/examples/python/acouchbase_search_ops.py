# tag::simple_query[]
import asyncio

from acouchbase.cluster import AsyncCluster
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
from couchbase.options import ClusterOptions
import couchbase.search as search


# NOTE: the travel-sample-index search index might need to be created
async def simple_query(cluster):
    try:
        result = cluster.search_query(
            "travel-sample-index", search.QueryStringQuery("swanky"))
        async for row in result:
            print("Found row: {}".format(row))
    except CouchbaseException as ex:
        print(ex)


async def main():
    cluster = await AsyncCluster.connect(
        "couchbase://your-ip",
        ClusterOptions(PasswordAuthenticator("Administrator", "password")))
    try:
        await simple_query(cluster)
    finally:
        await cluster.close()


asyncio.run(main())
# end::simple_query[]
