from datetime import timedelta
import logging
import sys

import couchbase
from couchbase.cluster import Cluster
from couchbase.options import (ClusterOptions,
                               ClusterOrphanReportingOptions,
                               ClusterTracingOptions)
from couchbase.auth import PasswordAuthenticator 
from couchbase.exceptions import UnAmbiguousTimeoutException

# configure logging
logging.basicConfig(filename='example.log',
                    filemode='w', 
                    level=logging.DEBUG,
                    format='%(levelname)s::%(asctime)s::%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
# setup couchbase logging
logger = logging.getLogger()
couchbase.configure_logging(logger.name, level=logger.level)

# tag::orphan_logging_config[]
orphan_opts = ClusterOrphanReportingOptions(
    emit_interval=timedelta(minutes=1),
    sample_size=10
)

authenticator = PasswordAuthenticator("Administrator", "password")
cluster_opts = ClusterOptions(authenticator, orphan_reporting_options=orphan_opts)

cluster = Cluster.connect("couchbase://your-ip", cluster_opts)
# end::orphan_logging_config[]
collection = cluster.bucket("beer-sample").default_collection()

for _ in range(100):
    try:
        # set timeout low to see orphan response
        collection.get("21st_amendment_brewery_cafe", timeout=timedelta(
            microseconds=1))
    except UnAmbiguousTimeoutException:
        pass
