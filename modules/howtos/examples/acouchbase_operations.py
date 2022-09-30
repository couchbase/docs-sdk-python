from couchbase.exceptions import (
    CouchbaseException, DocumentNotFoundException, ParsingFailedException)

# used to obtain the event loop
from acouchbase.cluster import get_event_loop

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
from acouchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator


async def get_couchbase():
    cluster = Cluster(
        "couchbase://localhost",
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
        result = cluster.search_query(
            "travel-sample-index", search.QueryStringQuery("swanky"))

        async for row in result:
            print("Found row: {}".format(row))
        print("Reported total rows: {}".format(
            result.metadata().metrics.total_rows))

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

loop = get_event_loop()
cluster, bucket = loop.run_until_complete(get_couchbase())
# get a reference to the default collection, required for older Couchbase server versions
cb_coll_default = bucket.default_collection()
# get a reference a named collection
cb_coll = bucket.scope("inventory").collection("hotel")

loop.run_until_complete(kv_operations(cb_coll))
loop.run_until_complete(sub_doc_operations(cb_coll))
loop.run_until_complete(n1ql_query(cluster))
loop.run_until_complete(search_query(cluster))
loop.run_until_complete(analytics_query(cluster))
