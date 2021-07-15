from couchbase.cluster import Cluster, ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.bucket import ViewOptions, ViewScanConsistency
from couchbase.management.views import DesignDocumentNamespace

cluster = Cluster.connect(
    "couchbase://localhost",
    ClusterOptions(PasswordAuthenticator("Administrator", "password")))
bucket = cluster.bucket("travel-sample")

"""
Sample view:
ddoc name:  dev_landmarks-by-country
name:       by_country

Map:
function (doc, meta) {
  if(doc.type == "landmark" && doc.country){
    emit(doc.country, null);
  }
}

Sample view:
ddoc name:  dev_landmarks-by-name
name:       by_name

Map:
function (doc, meta) {
  if(doc.type == "landmark" && doc.name){
    emit(doc.name, null);
  }
}
"""

# tag::landmarks_by_name[]
result = bucket.view_query("dev_landmarks-by-name",
                           "by_name",
                           ViewOptions(key="Circle Bar",
                                       namespace=DesignDocumentNamespace.DEVELOPMENT))
# end::landmarks_by_name[]

# tag::landmarks_by_country[]
result = bucket.view_query("dev_landmarks-by-country",
                           "by_country",
                           ViewOptions(startkey="U",
                                       limit=10,
                                       namespace=DesignDocumentNamespace.DEVELOPMENT,
                                       scan_consistency=ViewScanConsistency.REQUEST_PLUS))
# end::landmarks_by_country[]

# tag::iterating[]
for row in result.rows():
    print("Landmark named {} has documentID: {}".format(row.key, row.id))
# end::iterating[]