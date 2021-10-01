from couchbase.cluster import Cluster, PasswordAuthenticator
from couchbase.exceptions import CouchbaseException

cluster = Cluster("couchbase://localhost",
                  authenticator=PasswordAuthenticator("Administrator", "password"))

try:
    # tag::n1ql-query[]
    result = cluster.query("SELECT \"Hello World\" as greeting")
    for row in result.rows():
        print(row)
    # end::n1ql-query[]
except CouchbaseException as ex:
    import traceback
    traceback.print_exc()
