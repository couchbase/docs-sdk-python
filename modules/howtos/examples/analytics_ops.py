import uuid

# tag::analytics_basic_example[]
from couchbase.cluster import Cluster, ClusterOptions, AnalyticsOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
from couchbase.analytics import AnalyticsScanConsistency

cluster = Cluster.connect(
    "couchbase://localhost",
    ClusterOptions(PasswordAuthenticator("Administrator", "password")))
bucket = cluster.bucket("travel-sample")
collection = bucket.default_collection()

try:
    result = cluster.analytics_query("SELECT 'hello' AS greeting")

    for row in result.rows():
        print("Found row: {}".format(row))

    print("Reported execution time: {}".format(
        result.metadata().metrics().execution_time()))

except CouchbaseException as ex:
    import traceback
    traceback.print_exc()

# end::analytics_basic_example[]

# tag::positional[]
result = cluster.analytics_query(
    "SELECT count(*) FROM airports a WHERE a.country = ?",
    "France")
# end::positional[]

# tag::positional_options[]
result = cluster.analytics_query(
    "SELECT count(*) FROM airports a WHERE a.country = ?",
    AnalyticsOptions(positional_parameters=["France"]))
# end::positional_options[]

# tag::named_kwargs[]
result = cluster.analytics_query(
    "SELECT count(*) FROM airports a WHERE a.country = $country",
    country="France")
# end::named_kwargs[]

# tag::named_options[]
result = cluster.analytics_query(
    "SELECT count(*) FROM airports a WHERE a.country = $country",
    AnalyticsOptions(named_parameters={"country": "France"}))
# end::named_options[]

# tag::iterating[]
result = cluster.analytics_query(
    "SELECT a.* FROM airports a LIMIT 10")

# iterate over rows
for row in result:
    # each row is an instance of the query call
    print("Found row: {}".format(row))
# end::iterating[]

# tag::print_metrics[]
result = cluster.analytics_query("SELECT 1=1")

print("Execution time: {}".format(
    result.metadata().metrics().execution_time()))
# end::print_metrics[]

# tag::scan_consistency[]
result = cluster.analytics_query(
    "SELECT count(*) FROM airports a WHERE a.country = 'France'",
    AnalyticsOptions(scan_consistency=AnalyticsScanConsistency.REQUEST_PLUS))
# end::scan_consistency[]

# tag::client_context_id[]
result = cluster.analytics_query(
    "SELECT count(*) FROM airports a WHERE a.country = 'France'",
    AnalyticsOptions(client_context_id="user-44{}".format(uuid.uuid4())))
# end::client_context_id[]

# tag::priority[]
result = cluster.analytics_query(
    "SELECT count(*) FROM airports a WHERE a.country = 'France'",
    AnalyticsOptions(priority=True))
# end::priority[]

# tag::read_only[]
result = cluster.analytics_query(
    "SELECT count(*) FROM airports a WHERE a.country = 'France'",
    AnalyticsOptions(read_only=True))
# end::read_only[]

# tag::handle_collection[]
result = cluster.analytics_query(
    "SELECT airportname, country FROM `travel-sample`.inventory.airport a WHERE a.country = 'France' LIMIT 3")
# end::handle_collection[]

# tag::handle_scope[]
scope = bucket.scope("inventory")
result = scope.analytics_query(
    "SELECT airportname, country FROM airport a WHERE a.country = 'France' LIMIT 3")
# end::handle_scope[]
