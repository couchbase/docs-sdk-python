#!/usr/bin/env python

# tag::auth[]
from couchbase.auth import CertificateAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions

import os.path

# point to certificates, keys, and trust stores;
# for the purposes of this code,
# the script in etc/x509-cert will generate these
clientdir = "etc/x509-cert/SSLCA/clientdir"
options = dict(cert_path=os.path.join(clientdir, "client.pem"),
               trust_store_path=os.path.join(clientdir, "trust.pem"),
               key_path=os.path.join(clientdir, "client.key"))

opts = ClusterOptions(CertificateAuthenticator(**options))
cluster = Cluster('couchbase://your-ip', opts)
# end::auth[]
