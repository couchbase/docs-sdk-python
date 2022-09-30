# tag::simple_query[]
# **IMPORTANT** need to do this import prior to importing the reactor (new to the Python 4.x SDK)
import txcouchbase
from twisted.internet import reactor

from txcouchbase.cluster import TxCluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
import couchbase.search as search


def handle_query_results(result):
    for r in result.rows():
        print("query row: {}".format(r))

    reactor.stop()


def on_streaming_error(error):
    print("Streaming operation had an error.\nError: {}".format(error))
    reactor.stop()

# NOTE: the travel-sample-index search index might need to be created
def on_connect_ok(result, cluster):
    # create a bucket object
    bucket = cluster.bucket("travel-sample")
    # create a collection object
    cb = bucket.default_collection()

    d = cluster.search_query("travel-sample-index", search.QueryStringQuery("swanky"))
    d.addCallback(handle_query_results).addErrback(on_streaming_error)


def on_connect_err(error):
    print("Unable to connect.\n{}".format(error))


cluster = TxCluster("couchbase://localhost",
                    ClusterOptions(PasswordAuthenticator("Administrator", "password")))

# wait for connect
cluster.on_connect().addCallback(on_connect_ok, cluster).addErrback(on_connect_err)

reactor.run()
# end::simple_query[]
