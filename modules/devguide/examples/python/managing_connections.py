# requires:
#  - a local couchbase server with
#      username/password
#      travel-sample
#      beer-sample
#  - /etc/hosts (or C:\Windows\System32\Drivers\etc\hosts on Windows)
#      with `127.0.0.1 node2.example.com`

from acouchbase.cluster import AsyncCluster
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator

class ManagingConnections(object):
    def test_simpleconnect(self):

      print("simpleconnect")
      #tag::simpleconnect[]
      cluster = Cluster.connect("couchbase://your-ip", ClusterOptions(PasswordAuthenticator("Administrator", "password")))
      bucket = cluster.bucket("travel-sample")
      collection = bucket.default_collection()

      # You can access multiple buckets using the same Cluster object.
      another_bucket = cluster.bucket("beer-sample")

      # You can access collections other than the default
      # if your version of Couchbase Server supports this feature.
      customer_a = bucket.scope("customer-a")
      widgets = customer_a.collection("widgets")
      #end::simpleconnect[]

      # For a graceful shutdown, disconnect from the cluster when the program ends.
      cluster.close()


    def test_multinodeconnect(self):
      print("multinodeconnect")
      #tag::multinodeconnect[]
      cluster = Cluster.connect("couchbase://node1.example.com,node2.example.com", ClusterOptions(PasswordAuthenticator("Administrator", "password")))
      #end::multinodeconnect[]


    def test_connectionstringparams(self):
      print("connectionstringparams")
      #tag::connectionstringparams[]
      cluster = Cluster.connect(
          "couchbase://your-ip?compression=on&log_redaction=on", ClusterOptions(PasswordAuthenticator("Administrator", "password")))
      #end::connectionstringparams[]

    async def test_async(self):
      print("asynccluster")
      #tag::asynccluster[]
      cluster = await AsyncCluster.connect("couchbase://your-ip", ClusterOptions(PasswordAuthenticator("Administrator", "password")))
      bucket = cluster.bucket("travel-sample")

      # For a graceful shutdown, disconnect from the cluster when the program ends.
      await cluster.close()
      #end::asynccluster[]

      print("tls")
      #tag::tls[]
      cluster = Cluster.connect("couchbases://your-ip", ClusterOptions(PasswordAuthenticator("Administrator","password",cert_path="/path/to/cluster.crt")))
      #end::tls[]

      print("dnssrv")
      # dns srv is enabled by default in the C++ core
      #tag::dnssrv[]
      auth = PasswordAuthenticator("Administrator", "password")
      opts = ClusterOptions(auth, enable_dns_srv=True)
      #end::dnssrv[]

example = ManagingConnections()
example.test_simpleconnect()
## Test env is only 1 node
#example.test_multinodeconnect()
example.test_connectionstringparams()
# example.test_async() # TODO: DOC-9100
