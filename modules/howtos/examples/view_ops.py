from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, ViewOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.bucket import ViewScanConsistency
from couchbase.management.views import (
    View,
    DesignDocument,
    DesignDocumentNamespace)

cluster = Cluster.connect(
    "couchbase://your-ip",
    ClusterOptions(PasswordAuthenticator("Administrator", "password")))
bucket = cluster.bucket("travel-sample")

# Create views
view_manager = bucket.view_indexes()

landmarks_by_country = DesignDocument(
    name="dev_landmarks-by-country",
    views={
        "by_country": View(
            map='function (doc, meta) {if(doc.type == "landmark" && doc.country){emit(doc.country, null);}}')})

view_manager.upsert_design_document(
    landmarks_by_country, DesignDocumentNamespace.DEVELOPMENT)

view_manager.publish_design_document("landmarks-by-country")

landmarks_by_name = DesignDocument(
    name="dev_landmarks-by-name",
    views={
        "by_name": View(
            map='function (doc, meta) {if(doc.type == "landmark" && doc.name){emit(doc.name, null);}}')})

view_manager.upsert_design_document(
    landmarks_by_name, DesignDocumentNamespace.DEVELOPMENT)
view_manager.publish_design_document("landmarks-by-name")

# tag::landmarks_by_name[]
result = bucket.view_query("landmarks-by-name",
                           "by_name",
                           ViewOptions(key="Circle Bar",
                                       namespace=DesignDocumentNamespace.PRODUCTION))
# end::landmarks_by_name[]

# tag::landmarks_by_country[]
result = bucket.view_query("landmarks-by-country",
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