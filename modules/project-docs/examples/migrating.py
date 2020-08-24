from datetime import timedelta
from couchbase.cluster import Cluster
from couchbase.collection import GetOptions
class Migrating(object):
    pass

#tag::timeoutbuilder[]
# SDK 3 equivalent
cluster=Cluster("couchbases://10.192.1.104")
collection=cluster.bucket("default").default_collection()
collection.timeout=5
#end::timeoutbuilder[]

# not applicable
#natag::shutdown[]
# ClusterEnvironment env = ClusterEnvironment.create();
# Cluster cluster = Cluster.connect(
#     "127.0.0.1",
#                   // pass the custom environment through the cluster options
# clusterOptions("user", "pass").environment(env)
# );
#
# // first disconnect, then shutdown the environment
# cluster.disconnect();
# env.shutdown();
#naend::shutdown[]


#natag::sysprops[]
# not applicable
# Will set the max http connections to 23
# System.setProperty("com.couchbase.env.io.maxHttpConnections", "23");
# Cluster.connect("127.0.0.1", "user", "pass");
#
# #This is equivalent to
# ClusterEnvironment env = ClusterEnvironment \
#     .builder() \
#     .ioConfig(IoConfig.maxHttpConnections(23)) \
#     .build();
#naend::sysprops[]

from couchbase.cluster import *
from couchbase_core.cluster import PasswordAuthenticator
from couchbase_v2 import COMPRESS_INOUT
#tag::connstr[]
# Will set the compression type to inout
Cluster.connect(
    "couchbases://127.0.0.1?compression=inout",ClusterOptions(PasswordAuthenticator(
    "user",
    "pass")))

# This is equivalent to
collection.compression = COMPRESS_INOUT
#end::connstr[]

#tag::rbac[]
# add convenience overload when available
Cluster.connect("couchbases://127.0.0.1", ClusterOptions(PasswordAuthenticator("username", "password")))
#end::rbac[]

#tag::rbac-full[]
Cluster.connect(
    "couchbases://127.0.0.1",
    ClusterOptions(PasswordAuthenticator("username", "password")))
#end::rbac-full[]

from couchbase_core.cluster import  CertAuthenticator
import os
#tag::certauth[]
cert_dir=os.path.join(os.path.curdir,"cert_dir")

Cluster.connect("couchbases://127.0.0.1", ClusterOptions(
    CertAuthenticator(cert_path="cert.pem",
                      key_path="key.crt",
                      trust_store_path="trust_store.pem"
)))
#end::certauth[]

#tag::simpleget[]
cluster = Cluster.connect("couchbases://127.0.0.1", ClusterOptions(PasswordAuthenticator("user", "pass")))
bucket = cluster.bucket("travel-sample")
collection = bucket.default_collection()

get_result = collection.get("airline_10")

#end::simpleget[]

cluster = Cluster.connect("couchbases://127.0.0.1", ClusterOptions(PasswordAuthenticator("user", "pass")))
bucket = cluster.bucket("travel-sample")
collection = bucket.default_collection()

# tag::upsertandget[]
upsert_result = collection.upsert("mydoc-id", {})
get_result = collection.get("mydoc-id")
# end::upsertandget[]

from couchbase_v2.bucket import Bucket

# tag::upsertandget_sdk2[]
# SDK 2 upsert and get
bucket = Bucket("couchbases://127.0.0.1/default")
upsert_result = bucket.upsert("mydoc-id", {})
get_result = bucket.get("mydoc-id")
# end::upsertandget_sdk2[]

import couchbase_tests.base

#natag::rawjson[]
# TODO: update when implemented
from couchbase.collection import UpsertOptions
from couchbase_core.transcoder import Transcoder

class RawJSONTranscoder(Transcoder):
    pass

content = "{}".encode("UTF_8")
upsert_result = collection.upsert(
    "mydoc-id",
    content,
    UpsertOptions(transcoder=RawJSONTranscoder))

#naend::rawjson[]

class TimeoutTest(couchbase_tests.base.CollectionTestCase):

    def test_customtimeout(self):
#tag::customtimeout[]
# SDK 3 custom timeout
        get_result = collection.get(
            "mydoc-id",
            GetOptions(timeout=timedelta(seconds=5)))
        #tag::test[]
        self.assertEquals("fish",get_result.content_as[str])
        #end::test[]
#end::customtimeout[]

from couchbase_v2.bucket import Bucket
bucket=Bucket("couchbase://127.0.0.1")
#tag::querysimple_sdk2[]
# SDK 2 simple query
query_result = bucket.query("select * from `travel-sample` limit 10")
for row in query_result:
    value = row.value
#end::querysimple_sdk2[]

#tag::querysimple[]
# SDK 3 simple query
query_result = cluster.query("select * from `travel-sample` limit 10")
for value in query_result:
    #...
    pass
#end::querysimple[]

from couchbase_v2.bucket import Bucket
bucket=Bucket("couchbase://127.0.0.1")
# tag::queryparameterized_sdk2[]
# SDK 2 named parameters
bucket.query(
    "select * from bucket where type = $type",
    type="airport")

# SDK 2 positional parameters
bucket.query(
    "select * from bucket where type = $1",
    "airport")
# end::queryparameterized_sdk2[]
del bucket

# tag::queryparameterized[]
# SDK 3 named parameters
from couchbase.cluster import QueryOptions
cluster.query(
    "select * from bucket where type = $type",
    QueryOptions(named_parameters={"type": "airport"}))

# SDK 3 positional parameters
cluster.query(
    "select * from bucket where type = $1",
    QueryOptions(positional_parameters=["airport"]))
#end::queryparameterized[]

#tag::analyticssimple[]
# SDK 3 simple analytics query
analytics_result = cluster.analytics_query("select * from dataset")
for value in analytics_result:
    #...
    pass
#end::analyticssimple[]

#tag::analyticsparameterized[]
from couchbase.cluster import AnalyticsOptions
# SDK 3 named parameters for analytics
cluster.analytics_query(
        "select * from dataset where type = $type",
        AnalyticsOptions(named_parameters={"type": 'airport'}))

# SDK 3 positional parameters for analytics
cluster.analytics_query(
    "select * from dataset where type = $1",
    AnalyticsOptions(positional_parameters=["airport"]))
#end::analyticsparameterized[]


#tag::analyticsparameterized_args_kwargs[]
# SDK 3 named parameters for analytics
# TODO: enable when implemented, still offering old style *args, **kwargs interface
cluster.analytics_query(
    "select * from dataset where type = $type",
    type='airport')

# SDK 3 positional parameters for analytics
cluster.analytics_query(
    "select * from dataset where type = $1",
    ["airport"])
#naend::analyticsparameterized_args_kwargs[]

#tag::analyticsparameterized_args_kwargs[]

# SDK 2 error check
analyticsQueryResult = cluster.query("select * from foo")
if not analyticsQueryResult.errors():
    # errors contain [{"msg":"Cannot find dataset foo in dataverse Default nor an alias with name foo! (in line 1, at column 15)","code":24045}]
    pass

#tag::searchsimple[]
# SDK 3 search query
from couchbase.cluster import SearchOptions
search_result = cluster.search_query(
    "indexname",
    "airports",
    SearchOptions(timeout=timedelta(seconds=2),limit=5,fields=["a", "b", "c"]))
for row in search_result:
    # ...
    pass
#end::searchsimple[]

from couchbase_core.fulltext import Facet, TermFacet, DateFacet, NumericFacet
#natag::searchcheck_args_kwargs[]
search_result = cluster.search_query(
        "myindex",
        facets={'searchstring':Facet(),queryString("searchstring")})#.)
if search_result.metadata().error_count()==0:
    # no errors present, so full data got returned
    pass
#naend::searchcheck_args_kwargs[]

from couchbase.bucket import ViewOptions

bucket=cluster.bucket("fred")
#tag::viewquery[]
# SDK 3 view query
view_result = bucket.view_query(
    "design",
    "view",
    ViewOptions(limit=5,skip=2,timeout=timedelta(seconds=10)))
for row in view_result:
    # ...
    pass
#end::viewquery[]
