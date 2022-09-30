
# tag::txcouchbase_imports[]
# **IMPORTANT** need to do this import prior to importing the reactor (new to the Python 4.x SDK)
import txcouchbase
from twisted.internet import reactor

# needed for FTS support
import couchbase.search as search

# needed for sub-document operations
import couchbase.subdocument as SD

# used for analytics operations
from couchbase.analytics import AnalyticsOptions

# used to support SQL++ (N1QL) query
from couchbase.options import QueryOptions

# needed for cluster creation
from couchbase.auth import PasswordAuthenticator
from txcouchbase.cluster import TxCluster

# used for handling result objects
from couchbase.result import GetResult, LookupInResult
# end::txcouchbase_imports[]

# tag::kv[]
def on_kv_ok(result):
    if isinstance(result, GetResult):
        print("Document: {}".format(result.content_as[dict]))
    else:
        print("CAS: {}".format(result.cas))


def on_kv_error(error):
    print("Operation had an error.\nError: {}".format(error))


def kv_operations(collection):
    key = "hotel_10025"
    collection.get(key).addCallback(on_kv_ok).addErrback(on_kv_error)

    new_hotel = {
        "title": "Couchbase",
        "name": "The Couchbase Hotel",
        "address": "Pennington Street",
        "directions": None,
        "phone": "+44 1457 855449",
    }

    collection.upsert("hotel_98765", new_hotel).addCallback(
        on_kv_ok).addErrback(on_kv_error)

    collection.get("not-a-key").addCallback(on_kv_ok).addErrback(on_kv_error)
# end::kv[]


# tag::sub_doc[]
def on_sd_ok(result, idx=0):
    if isinstance(result, LookupInResult):
        print("Sub-document: {}".format(result.content_as[dict](idx)))
    else:
        print("CAS: {}".format(result.cas))


def on_sd_error(error):
    print("Operation had an error.\nError: {}".format(error))


def sub_doc_operations(collection):
    key = "hotel_10025"

    collection.lookup_in(key, [SD.get("reviews[0].ratings")]).addCallback(
        on_sd_ok).addErrback(on_sd_error)

    collection.mutate_in(key, [SD.replace("reviews[0].ratings.Rooms", 3.5)]).addCallback(
        on_sd_ok).addErrback(on_sd_error)
# end::sub_doc[]


def on_streaming_error(error):
    print("Streaming operation had an error.\nError: {}".format(error))

# tag::n1ql[]
def handle_n1ql_results(result):
    for r in result.rows():
        print("Query row: {}".format(r))


def n1ql_query(cluster):
    d = cluster.query(
        "SELECT h.* FROM `travel-sample`.inventory.hotel h WHERE h.country=$country LIMIT 2",
        QueryOptions(named_parameters={"country": "United Kingdom"}))
    d.addCallback(handle_n1ql_results).addErrback(on_streaming_error)
# end::n1ql[]

# NOTE: the travel-sample-index search index might need to be created
# tag::search[]
def handle_search_results(result):
    for r in result.rows():
        print("Search row: {}".format(r))


def search_query(cluster):
    d = cluster.search_query(
        "travel-sample-index", search.QueryStringQuery("swanky"))
    d.addCallback(handle_search_results).addErrback(on_streaming_error)
# end::search[]

# NOTE: the analytics dataset might need to be created
# tag::analytics[]
def handle_analytics_results(result):
    for r in result.rows():
        print("Analytics row: {}".format(r))

def analytics_query(cluster):
    d = cluster.analytics_query(
        "SELECT id, country FROM `travel-sample`.inventory.airports a WHERE a.country = $country LIMIT 10",
        AnalyticsOptions(named_parameters={"country": "France"}))
    d.addCallback(handle_analytics_results).addErrback(on_streaming_error)
# end::analytics[]


def do_stuff(cluster, bucket, cb_coll, cb_coll_default):
    kv_operations(cb_coll)
    sub_doc_operations(cb_coll)
    n1ql_query(cluster)
    search_query(cluster)
    analytics_query(cluster)

# tag::create[]
def on_connect_ok(result, cluster):
    # create a bucket object
    bucket = cluster.bucket('travel-sample')
    # get a reference to the default collection, required for older Couchbase server versions
    cb_coll_default = bucket.default_collection()
    # get a reference a named collection
    cb_coll = bucket.scope("inventory").collection("hotel")
    do_stuff(cluster, bucket, cb_coll, cb_coll_default)


def on_connect_err(error):
    print("Unable to connect.\n{}".format(error))


# create a cluster object
cluster = TxCluster('couchbase://localhost',
                    authenticator=PasswordAuthenticator(
                        'Administrator',
                        'password'))

# wait for connect
cluster.on_connect().addCallback(on_connect_ok, cluster).addErrback(on_connect_err)
# end::create[]

reactor.callLater(10, reactor.stop)
reactor.run()
