# requires:
#  - a local couchbase server with
#      username/password
#      travel-sample
#      beer-sample
#  - /etc/hosts (or C:\Windows\System32\Drivers\etc\hosts on Windows)
#      with `127.0.0.1 node2.example.com`

from couchbase.cluster import Cluster, ClusterOptions
from couchbase_core.cluster import PasswordAuthenticator

class ManagingConnections(object):
    def test_simpleconnect(self):

      print("simpleconnect")
      #tag::simpleconnect[]
      cluster = Cluster.connect("couchbase://127.0.0.1", ClusterOptions(PasswordAuthenticator("username", "password")))
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
      cluster.disconnect()


    def test_multinodeconnect(self):
      print("multinodeconnect")
      #tag::multinodeconnect[]
      cluster = Cluster.connect("couchbase://node1.example.com,node2.example.com", ClusterOptions(PasswordAuthenticator("username", "password")))
      #end::multinodeconnect[]

    #
    # def test_customenv(self):
    #   #tag::customenv[]
    #   env = ClusterEnvironment.builder()
    #       .build();
    #   # Customize client settings by calling methods on the builder
    #
    #   # Create a cluster using the environment's custom client settings.
    #   cluster = Cluster.connect("couchbase://127.0.0.1", ClusterOptions
    #       .clusterOptions("username", "password")
    #       .environment(env))
    #
    #   # Shut down gracefully. Shut down the environment
    #   # after all associated clusters are disconnected.
    #   cluster.disconnect()
    #   env.shutdown()
    #   #end::customenv[]
    #
    #
    # def test_shareclusterenv(self):
    #   #tag::shareclusterenvironment[]
    #   env = ClusterEnvironment.builder()\
    #       .timeoutConfig(TimeoutConfig.kvTimeout(Duration.ofSeconds(5)))\
    #       .build()
    #
    #   clusterA = Cluster.connect(
    #       "clusterA.example.com",
    #       ClusterOptions("username", "password")
    #           .environment(env));
    #
    #   clusterB = Cluster.connect(
    #       "clusterB.example.com",
    #       ClusterOptions("username", "password")
    #           .environment(env));

    # # ...
    #
    #   # For a graceful shutdown, disconnect from the clusters
    #   # AND shut down the custom environment when then program ends.
    #   clusterA.disconnect();
    #   clusterB.disconnect();
    #   env.shutdown();
    #end::shareclusterenvironment[]

#
#     // todo use this example when beta 2 is released.
# //    {
# //      // #tag::seednodes[]
# //      int customKvPort = 12345;
# //      int customManagerPort = 23456
# //      Set<SeedNode> seedNodes = new HashSet<>(Arrays.asList(
# //          SeedNode.create("127.0.0.1",
# //              Optional.of(customKvPort),
# //              Optional.of(customManagerPort))))
# //
#
# //      Cluster cluster = Cluster.connect(seedNodes, "username", "password")
# //      // #end::customconnect[]
# //    }

    def test_connectionstringparams(self):
      print("connectionstringparams")
      #tag::connectionstringparams[]
      cluster = Cluster.connect(
          "couchbase://127.0.0.1?compression=on&log_redaction=on", ClusterOptions(PasswordAuthenticator("username", "password")))
      #end::connectionstringparams[]

    def test_async(self):
      print("blockingtoasync")
      #tag::blockingtoasync[]
      cluster = Cluster.connect("couchbase://127.0.0.1", ClusterOptions(PasswordAuthenticator("username", "password")))
      bucket = cluster.bucket("travel-sample")

      # Same API as Bucket, but completely async with asyncio Futures
      from acouchbase.bucket import Bucket
      async_bucket=Bucket("couchbase://127.0.0.1/default")

      cluster.disconnect()
      #end::blockingtoasync[]

      print("reactivecluster")
      #tag::reactivecluster[]
      from acouchbase.bucket import Bucket
      cluster = Cluster("couchbase://127.0.0.1", ClusterOptions(PasswordAuthenticator("username", "password")),bucket_class=Bucket)
      bucket = cluster.bucket("travel-sample")

      # A reactive cluster's disconnect methods returns a Mono<Void>.
      # Nothing actually happens until you subscribe to the Mono.
      # The simplest way to subscribe is to await completion by calling call `block()`.
      cluster.disconnect()
      #end::reactivecluster[]

      print("asynccluster")
      #tag::asynccluster[]
      cluster = Cluster.connect("couchbase://127.0.0.1", ClusterOptions(PasswordAuthenticator("username", "password")))
      bucket = cluster.bucket("travel-sample")

      # An async cluster's disconnect methods returns a CompletableFuture<Void>.
      # The disconnection starts as soon as you call disconnect().
      # The simplest way to wait for the disconnect to complete is to call `join()`.
      cluster.disconnect().join()
      #end::asynccluster[]

      print("tls")
      #tag::tls[]
      cluster = Cluster("couchbases://127.0.0.1",ClusterOptions(PasswordAuthenticator("username","password",cert_path="/path/to/cluster.crt")))
      #end::tls[]

      print("dnssrv")
      #tag::dnssrv[]
      env = ClusterEnvironment.builder() \
          .ioConfig(IoConfig.enableDnsSrv(true)) \
          .build()
      #end::dnssrv[]

example = ManagingConnections()
example.test_simpleconnect()
example.test_multinodeconnect()
example.test_connectionstringparams()
# example.test_async() # TODO: DOC-9100
