from typing import Union
from couchbase_core import IterableWrapper
from couchbase.analytics import AnalyticsResult

# Requires:
#   `travel-sample` bucket
#     *  CREATE DATASET `airports` ON `travel-sample` where `type` = "airport";
#     *  ALTER COLLECTION `travel-sample`.`inventory`.`airport` ENABLE ANALYTICS;

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
        cluster = Cluster.connect("couchbase://your-ip", ClusterOptions(PasswordAuthenticator("Administrator", "password")))

        try:
            result = cluster.analytics_query("select \"hello\" as greeting")

            for row in result.rows():
                print("Found row: " + str(row))

            print("Reported execution time: "
                  + result.metrics["executionTime"])
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
        result = cluster.analytics_query(
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
            "select * from airports limit 10"
        )
        for row in result.rows():
            print("Found row: " + str(row))

        # end::rowsasobject[]

        print("handle-collection")
        # tag::handle-collection[]
        result = cluster.analytics_query('SELECT airportname, country FROM `travel-sample`.inventory.airport WHERE country="France" LIMIT 3')
        # end::handle-collection[]
        for row in result.rows():
            print("Found row: " + str(row))

        print("handle-scope")
        # tag::handle-scope[]
        bucket = cluster.bucket("travel-sample")
        scope = bucket.scope("inventory")
        print(dir(scope))
        result = scope.analytics_query('SELECT airportname, country FROM airport WHERE country="France" LIMIT 3')
        # end::handle-scope[]
        for row in result.rows():
            print("Found row: " + str(row))

        print("End")

Analytics().main([])
