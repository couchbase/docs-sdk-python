from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.management.views import View, DesignDocument, \
    DesignDocumentNamespace

# tag::create_view_mgr[]
cluster = Cluster(
    "couchbase://localhost",
    authenticator=PasswordAuthenticator(
        "Administrator",
        "password"))

# For Server versions 6.5 or later you do not need to open a bucket here
bucket = cluster.bucket("travel-sample")

view_manager = bucket.view_indexes()
# end::create_view_mgr[]

# tag::create_view[]
design_doc = DesignDocument(
    name="landmarks",
    views={
        "by_country": View(
            map="function (doc, meta) { if (doc.type == 'landmark') { emit([doc.country, doc.city], null); } }"),
        "by_activity": View(
            map="function (doc, meta) { if (doc.type == 'landmark') { emit(doc.activity, null); } }",
            reduce="_count")})

view_manager.upsert_design_document(
    design_doc, DesignDocumentNamespace.DEVELOPMENT)
# end::create_view[]

# tag::get_view[]
d_doc = view_manager.get_design_document(
    "landmarks", DesignDocumentNamespace.DEVELOPMENT)

print("Found design doc: {} w/ {} views.".format(d_doc.name, len(d_doc.views)))
# end::get_view[]

# tag::publish_view[]
view_manager.publish_design_document("landmarks")
# end::publish_view[]

# tag::drop_view[]
view_manager.drop_design_document(
    "landmarks", DesignDocumentNamespace.DEVELOPMENT)
# end::drop_view[]