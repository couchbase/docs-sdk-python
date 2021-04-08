from datetime import timedelta
import logging
import sys

from couchbase.cluster import Cluster, ClusterOptions, ClusterTracingOptions
from couchbase.auth import PasswordAuthenticator
from couchbase import enable_logging

# NOTE: for simple test to see output, drop the threshold
#         ex:  tracing_threshold_kv=timedelta(microseconds=1)

# tag::threshold_logging_config[]
# configure logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
# setup couchbase logging
enable_logging()

tracing_opts = ClusterTracingOptions(
    tracing_threshold_queue_size=10,
    tracing_threshold_kv=timedelta(milliseconds=500))

cluster_opts = ClusterOptions(authenticator=PasswordAuthenticator(
    "Administrator",
    "password"),
    tracing_options=tracing_opts)

cluster = Cluster(
    "couchbase://localhost",
    options=cluster_opts
)
# end::threshold_logging_config[]

collection = cluster.bucket("beer-sample").default_collection()

for _ in range(100):
    collection.get("21st_amendment_brewery_cafe")
