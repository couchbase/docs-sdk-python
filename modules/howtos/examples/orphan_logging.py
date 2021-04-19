from datetime import timedelta
import logging
import sys

from couchbase.cluster import Cluster, ClusterOptions, ClusterTracingOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import TimeoutException
from couchbase import enable_logging

# tag::orphan_logging_config[]
# configure logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
# setup couchbase logging
enable_logging()

tracing_opts = ClusterTracingOptions(
    # report interval
    tracing_orphaned_queue_flush_interval=timedelta(minutes=1),
    # sample size
    tracing_orphaned_queue_size=10
)

cluster_opts = ClusterOptions(authenticator=PasswordAuthenticator(
    "Administrator",
    "password"),
    tracing_options=tracing_opts)

cluster = Cluster(
    "couchbase://localhost",
    options=cluster_opts
)
# end::orphan_logging_config[]
collection = cluster.bucket("beer-sample").default_collection()

for _ in range(100):
    try:
        # set timeout low to see orphan response
        collection.get("21st_amendment_brewery_cafe", timeout=timedelta(
            microseconds=1))
    except TimeoutException:
        pass
