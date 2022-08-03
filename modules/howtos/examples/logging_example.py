# logging implemented in 4.0.2
# tag::logging[]
import logging
import traceback
from datetime import timedelta

import couchbase
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.diagnostics import ServiceType
from couchbase.exceptions import CouchbaseException
from couchbase.options import ClusterOptions, WaitUntilReadyOptions

# output log messages to example.log
logging.basicConfig(filename='example.log',
                    filemode='w', 
                    level=logging.DEBUG,
                    format='%(levelname)s::%(asctime)s::%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger()
couchbase.configure_logging(logger.name, level=logger.level)

cluster = Cluster('couchbase://localhost',
                  ClusterOptions(PasswordAuthenticator("Administrator", "password")))

cluster.wait_until_ready(timedelta(seconds=3),
                         WaitUntilReadyOptions(service_types=[ServiceType.KeyValue, ServiceType.Query]))

logger.info('Cluster ready.')

bucket = cluster.bucket("travel-sample")
coll = bucket.scope('inventory').collection('airline')
try:
    coll.get('not-a-key')
except CouchbaseException:
    logger.error(traceback.format_exc())

# end::logging[]
