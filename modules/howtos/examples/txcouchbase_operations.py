
from twisted.internet import reactor

from txcouchbase.cluster import TxCluster
from couchbase.cluster import QueryOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.result import GetResult, LookupInResult

# needed for sub-document operations
import couchbase.subdocument as SD

# needed for FTS support
import couchbase.search as search

# needed for
from couchbase.analytics import AnalyticsOptions


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


# tag::n1ql[]
def handle_n1ql_results(result):
    for r in result.rows():
        print("Query row: {}".format(r))


def n1ql_query(cluster):
    cluster.query(
        "SELECT h.* FROM `travel-sample`.inventory.hotel h WHERE h.country=$country LIMIT 2",
        QueryOptions(named_parameters={"country": "United Kingdom"})).addCallback(handle_n1ql_results)
# end::n1ql[]


# tag::search[]
def handle_search_results(result):
    for r in result.rows():
        print("Search row: {}".format(r))


def search_query(cluster):
    cluster.search_query(
        "travel-sample-index", search.QueryStringQuery("swanky")).addCallback(handle_search_results)
# end::search[]


# tag::analytics[]
def handle_analytics_results(result):
    for r in result.rows():
        print("Analytics row: {}".format(r))


def analytics_query(cluster):
    cluster.analytics_query(
        "SELECT id, country FROM `travel-sample`.inventory.airports a WHERE a.country = $country LIMIT 10",
        AnalyticsOptions(named_parameters={"country": "France"})).addCallback(handle_analytics_results)
# end::analytics[]


# tag::create[]
# create a cluster object
cluster = TxCluster(
    connection_string='couchbase://localhost',
    authenticator=PasswordAuthenticator(
        'Administrator',
        'password'))

# create a bucket object
bucket = cluster.bucket('travel-sample')
# end::create[]

# get a reference to the default collection, required for older Couchbase server versions
cb_coll_default = bucket.default_collection()
# get a reference a named collection
cb_coll = bucket.scope("inventory").collection("hotel")

kv_operations(cb_coll)
sub_doc_operations(cb_coll)
n1ql_query(cluster)
search_query(cluster)
analytics_query(cluster)

reactor.callLater(10, reactor.stop)
reactor.run()
