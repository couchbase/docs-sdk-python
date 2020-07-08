# tag::imports[]
from couchbase.cluster import Cluster
# end::imports[]
from couchbase.exceptions import CouchbaseException
from couchbase.cluster import AnalyticsOptions


class Analytics(object):

    def main(self, args):
        # tag::simple[]
        cluster = Cluster.connect("localhost", "Administrator", "password")
        try:
            result = cluster.analytics_query("select \"hello\" as greeting")

            for row in result.rows():
                print("Found row: " + row)

            print("Reported execution time: "
                  + result.metaData().metrics().executionTime())
        except CouchbaseException as ex:
            import traceback
            traceback.print_exc()
        # end::simple[]

        # tag::named[]
        result = cluster.analytics_query(
            "select count(*) from airports where country = $country",
            country="France")

        # end::named[]

        # tag::positional[]
        result = cluster.analytics_query(
            "select count(*) from airports where country = ?",
            "France")
        # end::positional[]

        # tag::scanconsistency[]
        result = cluster.analytics_query(
            "select ...",
            scan_consistency=AnalyticsScanConsistency.REQUEST_PLUS)
        # end::scanconsistency[]

        # tag::clientcontextid[]
        result = cluster.analyticsQuery(
        "select ...",
        analyticsOptions().clientContextId("user-44" + UUID.randomUUID().toString()))

        # end::clientcontextid[]

        # tag::priority[]
        result = cluster.analytics_query(
            "select ...",
            analyticsOptions().priority(true)
        )
        # end::priority[]

        # tag::readonly[]
        result = cluster.analyticsQuery(
            "select ...",
            readonly=True
        )
        # end::readonly[]

        # tag::printmetrics[]
        result = cluster.analytics_query("select 1=1")
        print(
            "Execution time: " + result.metaData().metrics().executionTime()
        )
        # end::printmetrics[]

        # tag::rowsasobject[]
        result = cluster.analytics_query(
            "select * from `travel-sample` limit 10"
        )
        for row in result.rows():
            print("Found row: " + row)

# end::rowsasobject[]
