# tag::simple_query[]
import asyncio

from acouchbase.cluster import AsyncCluster
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
from couchbase.options import AnalyticsOptions, ClusterOptions


# NOTE: the analytics dataset might need to be created
async def simple_query(cluster):
    try:
        result = cluster.analytics_query(
            "SELECT id, country FROM airports a WHERE a.country = $country LIMIT 10",
            AnalyticsOptions(named_parameters={"country": "France"}))
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
