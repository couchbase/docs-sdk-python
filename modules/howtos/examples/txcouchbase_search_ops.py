# tag::simple_query[]
from twisted.internet import reactor

from txcouchbase.cluster import TxCluster
from couchbase.cluster import ClusterOptions
from couchbase.auth import PasswordAuthenticator
import couchbase.search as search


def handle_query_results(result):
    for r in result.rows():
        print("query row: {}".format(r))

    reactor.stop()


cluster = TxCluster("couchbase://localhost",
                    ClusterOptions(PasswordAuthenticator("Administrator", "password")))

# create a bucket object
bucket = cluster.bucket("travel-sample")
# create a collection object
cb = bucket.default_collection()

d = cluster.search_query("travel-sample-index", search.QueryStringQuery("swanky"))
d.addCallback(handle_query_results)

reactor.run()
# end::simple_query[]
