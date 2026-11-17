import asyncio

from couchbase.exceptions import (
    CouchbaseException, DocumentNotFoundException, ParsingFailedException)

# needed for sub-document operations
import couchbase.subdocument as SD

# used to support SQL++ (N1QL) query
from couchbase.options import QueryOptions

# needed for FTS support
import couchbase.search as search

# used for analytics operations
from couchbase.options import AnalyticsOptions

# tag::create[]

# needed for cluster creation
from acouchbase.cluster import AsyncCluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator


async def get_couchbase():
    cluster = await AsyncCluster.connect(
        "couchbase://your-ip",
        ClusterOptions(PasswordAuthenticator("Administrator", "password")))
    bucket = cluster.bucket("travel-sample")
    await bucket.on_connect()

    return cluster, bucket
# end::create[]


# tag::kv[]
async def kv_operations(collection):
    key = "hotel_10025"
    res = await collection.get(key)
    hotel = res.content_as[dict]
    print("Hotel: {}".format(hotel))

    hotel["alias"] = "Hostel"
    res = await collection.upsert(key, hotel)
    print("CAS: {}".format(res.cas))

    # handle exception
    try:
        res = await collection.get("not-a-key")
    except DocumentNotFoundException as ex:
        print("Document not found exception caught!")
# end::kv[]


# tag::sub_doc[]
async def sub_doc_operations(collection):
    key = "hotel_10025"
    res = await collection.lookup_in(key,
                                     [SD.get("reviews[0].ratings")])

    print("Review ratings: {}".format(res.content_as[dict](0)))

    res = await collection.mutate_in(key,
                                     [SD.replace("reviews[0].ratings.Rooms", 3.5)])
    print("CAS: {}".format(res.cas))
# end::sub_doc[]


# tag::bulk[]
async def bulk_operations(collection):
    keys = ["hotel_10025", "hotel_10026", "hotel_10064"]
    results = await asyncio.gather(*[collection.get(key) for key in keys],
                                   return_exceptions=True)
    for key, res in zip(keys, results):
        if isinstance(res, CouchbaseException):
            print("Get failed for {}: {}".format(key, res))
        else:
            print("Hotel {}: {}".format(key, res.content_as[dict]["name"]))
# end::bulk[]


# tag::n1ql[]
async def n1ql_query(cluster):
    try:
        result = cluster.query(
            "SELECT h.* FROM `travel-sample`.inventory.hotel h WHERE h.country=$country LIMIT 10",
            QueryOptions(named_parameters={"country": "United Kingdom"}))

        async for row in result:
            print("Found row: {}".format(row))
    except ParsingFailedException as ex:
        print(ex)
    except CouchbaseException as ex:
        print(ex)
# end::n1ql[]

# NOTE: the travel-sample-index search index might need to be created
# tag::search[]
async def search_query(cluster):
    try:
        result = cluster.search(
            "travel-sample-index", search.SearchRequest.create(search.QueryStringQuery("swanky")))

        async for row in result:
            print(f"Found row: {row}")
        print(f"Reported total rows: {result.metadata().metrics().total_rows()}")

    except CouchbaseException as ex:
        print(ex)
# end::search[]

# NOTE: the analytics dataset might need to be created
# tag::analytics[]
async def analytics_query(cluster):
    try:
        result = cluster.analytics_query(
            "SELECT a.* FROM `travel-sample`.inventory.airports a WHERE a.country = $country LIMIT 10",
            AnalyticsOptions(named_parameters={"country": "France"}))
        async for row in result:
            print("Found row: {}".format(row))
    except CouchbaseException as ex:
        print(ex)
# end::analytics[]


# tag::run[]
async def main():
    cluster, bucket = await get_couchbase()
    # get a reference to the default collection, required for older Couchbase server versions
    cb_coll_default = bucket.default_collection()
    # get a reference a named collection
    cb_coll = bucket.scope("inventory").collection("hotel")

    try:
        await kv_operations(cb_coll)
        await sub_doc_operations(cb_coll)
        await bulk_operations(cb_coll)
        await n1ql_query(cluster)
        await search_query(cluster)
        await analytics_query(cluster)
    finally:
        await cluster.close()


asyncio.run(main())
# end::run[]
