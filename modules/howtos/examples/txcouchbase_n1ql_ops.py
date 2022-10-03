# tag::simple_query[]
# **IMPORTANT** need to do this import prior to importing the reactor (new to the Python 4.x SDK)
import txcouchbase
from twisted.internet import reactor

from txcouchbase.cluster import TxCluster
from couchbase.options import ClusterOptions, QueryOptions
from couchbase.auth import PasswordAuthenticator


def handle_query_results(result):
    for r in result.rows():
        print("query row: {}".format(r))
    reactor.stop()


def on_streaming_error(error):
    print("Streaming operation had an error.\nError: {}".format(error))
    reactor.stop()


def on_connect_ok(result, cluster):
    # create a bucket object
    bucket = cluster.bucket("travel-sample")
    # create a collection object
    cb = bucket.default_collection()

    d = cluster.query("SELECT ts.* FROM `travel-sample` ts WHERE ts.`type`=$type LIMIT 10",
                    QueryOptions(named_parameters={"type": "hotel"}))
    d.addCallback(handle_query_results).addErrback(on_streaming_error)


def on_connect_err(error):
    print("Unable to connect.\n{}".format(error))

cluster = TxCluster("couchbase://localhost",
                    ClusterOptions(PasswordAuthenticator("Administrator", "password")))

# wait for connect
cluster.on_connect().addCallback(on_connect_ok, cluster).addErrback(on_connect_err)


reactor.run()
# end::simple_query[]