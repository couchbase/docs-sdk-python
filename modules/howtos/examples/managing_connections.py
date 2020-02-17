from couchbase.cluster import Cluster, ClusterOptions
from couchbase_core.cluster import PasswordAuthenticator

class ManagingConnections(object):
    def test_simpleconnect(self):

      #tag::simpleconnect[]
      cluster = Cluster.connect("127.0.0.1", ClusterOptions(PasswordAuthenticator("username", "password")))
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
      #tag::multinodeconnect[]
      cluster = Cluster.connect("couchbase://192.168.56.101,192.168.56.102", ClusterOptions(PasswordAuthenticator("username", "password")))
      #end::multinodeconnect[]


    def test_customenv(self):
      #tag::customenv[]
      env = ClusterEnvironment.builder()
          .build();
      # Customize client settings by calling methods on the builder

      # Create a cluster using the environment's custom client settings.
      cluster = Cluster.connect("127.0.0.1", ClusterOptions
          .clusterOptions("username", "password")
          .environment(env))

      # Shut down gracefully. Shut down the environment
      # after all associated clusters are disconnected.
      cluster.disconnect()
      env.shutdown()
      #end::customenv[]


    def test_shareclusterenv(self):
      #tag::shareclusterenvironment[]
      env = ClusterEnvironment.builder()\
          .timeoutConfig(TimeoutConfig.kvTimeout(Duration.ofSeconds(5)))\
          .build()

      clusterA = Cluster.connect(
          "clusterA.example.com",
          ClusterOptions("username", "password")
              .environment(env));

      clusterB = Cluster.connect(
          "clusterB.example.com",
          ClusterOptions("username", "password")
              .environment(env));

      # ...

      # For a graceful shutdown, disconnect from the clusters
      # AND shut down the custom environment when then program ends.
      clusterA.disconnect();
      clusterB.disconnect();
      env.shutdown();
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

      #tag::connectionstringparams[]
      cluster = Cluster.connect(
          "127.0.0.1?io.maxHttpConnections=23&io.networkResolution=external", "username", "password")
      #end::connectionstringparams[]

      #tag::blockingtoasync[]
      cluster = Cluster.connect("127.0.0.1", "username", "password")
      bucket = cluster.bucket("travel-sample")

      # Same API as Bucket, but completely async with CompletableFuture
      asyncBucket = bucket.async()

      # Same API as Bucket, but completely reactive with Flux and Mono
      reactiveBucket = bucket.reactive()

      cluster.disconnect()
      #end::blockingtoasync[]

      #tag::reactivecluster[]
      from acouchbase.bucket import Bucket
      cluster = Cluster("127.0.0.1", ClusterOptions(PasswordAuthenticator("username", "password")),bucket_class=Bucket)
      bucket = cluster.bucket("travel-sample")

      # A reactive cluster's disconnect methods returns a Mono<Void>.
      # Nothing actually happens until you subscribe to the Mono.
      # The simplest way to subscribe is to await completion by calling call `block()`.
      cluster.disconnect()
      #end::reactivecluster[]

      #tag::asynccluster[]
      cluster = Cluster.connect("127.0.0.1", ClusterOptions(PasswordAuthenticator("username", "password")))
      bucket = cluster.bucket("travel-sample")

      # An async cluster's disconnect methods returns a CompletableFuture<Void>.
      # The disconnection starts as soon as you call disconnect().
      # The simplest way to wait for the disconnect to complete is to call `join()`.
      cluster.disconnect().join()
      #end::asynccluster[]


      #tag::tls[]
      cluster = Cluster("couchbases://127.0.0.1",ClusterOptions(PasswordAuthenticator("username","password",cert_path="/path/to/cluster.crt")))
      #end::tls[]

      #tag::dnssrv[]
      env = ClusterEnvironment.builder()
          .ioConfig(IoConfig.enableDnsSrv(true))
          .build()
       #end::dnssrv[]
