from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.bucket import PingOptions
from couchbase.diagnostics import PingState, ServiceType

# tag::check_connection[]
def ok(cluster):
    result = cluster.ping()
    for _, reports in result.endpoints.items():
        for report in reports:
            if not report.state == PingState.OK:
                return False
    return True
# end::check_connection[]


cluster = Cluster(
    "couchbase://your-ip",
    authenticator=PasswordAuthenticator(
        "Administrator",
        "password"))
# For Server versions 6.5 or later you do not need to open a bucket here
bucket = cluster.bucket("beer-sample")
collection = bucket.default_collection()

# tag::cluster_ping_latency[]
ping_result = cluster.ping()

for endpoint, reports in ping_result.endpoints.items():
    for report in reports:
        print(
            "{0}: {1} took {2}".format(
                endpoint.value,
                report.remote,
                report.latency))
# end::cluster_ping_latency[]

# tag::cluster_ping_as_json[]
ping_result = cluster.ping()
print(ping_result.as_json())
# end::cluster_ping_as_json[]

print("Cluster is okay? {}".format(ok(cluster)))

# tag::cluster_ping_n1ql[]
ping_result = cluster.ping(PingOptions(service_types=[ServiceType.Query]))
print(ping_result.as_json())
# end::cluster_ping_n1ql[]

# tag::cluster_diagnostics[]
diag_result = cluster.diagnostics()
print(diag_result.as_json())
# end::cluster_diagnostics[]

print("Cluster state: {}".format(diag_result.state))
