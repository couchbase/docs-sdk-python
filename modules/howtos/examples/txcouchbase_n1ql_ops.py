# tag::simple_query[]
from twisted.internet import reactor

from txcouchbase.cluster import TxCluster
from couchbase.cluster import ClusterOptions, QueryOptions
from couchbase.auth import PasswordAuthenticator


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

d = cluster.query("SELECT ts.* FROM `travel-sample` ts WHERE ts.`type`=$type LIMIT 10",
                  QueryOptions(named_parameters={"type": "hotel"}))
d.addCallback(handle_query_results)

reactor.run()
# end::simple_query[]