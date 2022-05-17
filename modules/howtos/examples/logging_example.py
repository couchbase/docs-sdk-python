# tag::logging[]
import logging
import sys

import couchbase
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
couchbase.enable_logging()

cluster = Cluster('couchbase://localhost',
                  ClusterOptions(PasswordAuthenticator("Administrator", "password")))

bucket = cluster.bucket("travel-sample")
coll = bucket.scope('inventory').collection('airline')
coll.upsert('key', ['value'])
# end::logging[]
