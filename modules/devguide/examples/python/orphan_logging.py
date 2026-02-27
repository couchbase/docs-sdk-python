from datetime import timedelta
import logging
import sys

import couchbase
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, ClusterTracingOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import UnAmbiguousTimeoutException

# tag::orphan_logging_config[]
# configure logging
logging.basicConfig(filename='example.log',
                    filemode='w', 
                    level=logging.DEBUG,
                    format='%(levelname)s::%(asctime)s::%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
# setup couchbase logging
logger = logging.getLogger()
couchbase.configure_logging(logger.name, level=logger.level)

tracing_opts = ClusterTracingOptions(
    # report interval
    tracing_orphaned_queue_flush_interval=timedelta(minutes=1),
    # sample size
    tracing_orphaned_queue_size=10
)

authenticator = PasswordAuthenticator("Administrator", "password")

cluster = Cluster("couchbase://your-ip", ClusterOptions(authenticator,tracing_options=tracing_opts))
# end::orphan_logging_config[]
collection = cluster.bucket("beer-sample").default_collection()

for _ in range(100):
    try:
        # set timeout low to see orphan response
        collection.get("21st_amendment_brewery_cafe", timeout=timedelta(
            microseconds=1))
    except UnAmbiguousTimeoutException:
        pass
