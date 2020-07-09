from typing import Union
from couchbase_core import IterableWrapper
from couchbase.analytics import AnalyticsResult

# tag::imports[]

from couchbase.cluster import Cluster, ClusterOptions
from couchbase.exceptions import CouchbaseException
from couchbase.cluster import AnalyticsOptions, PasswordAuthenticator


# end::imports[]


class AnalyticsScanConsistency(object):
    pass


class Analytics(object):

    def main(self, args):
        # tag::simple[]
        cluster = Cluster.connect("localhost", ClusterOptions(PasswordAuthenticator("Administrator", "password")))
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

        # TODO: uncoment pending https://issues.couchbase.com/browse/PYCBC-976
        # # tag::scanconsistency[]
        # result = cluster.analytics_query(
        #     "select ...",
        #     scan_consistency=AnalyticsScanConsistency.REQUEST_PLUS)
        # # end::scanconsistency[]

        # tag::clientcontextid[]
        import uuid
        result = cluster.analyticsQuery(
        "select ...",
        AnalyticsOptions(client_context_id="user-44{}".format(uuid.uuid4())))

        # end::clientcontextid[]

        # tag::priority[]
        result = cluster.analytics_query(
            "select ...",
            AnalyticsOptions(priority=True)
        )
        # end::priority[]

        # tag::readonly[]
        result = cluster.analytics_query(
            "select ...",
            readonly=True
        )
        # end::readonly[]

        # TODO: uncomment pending https://issues.couchbase.com/browse/PYCBC-977
        # # tag::printmetrics[]
        # result = cluster.analytics_query("select 1=1")  # type: Union[AnalyticsResult,IterableWrapper]
        # print(
        #     "Execution time: " + result.metadata().metrics().executionTime()
        # )
        # # end::printmetrics[]
        #

        # tag::rowsasobject[]
        result = cluster.analytics_query(
            "select * from `travel-sample` limit 10"
        )
        for row in result.rows():
            print("Found row: " + row)

        # end::rowsasobject[]
