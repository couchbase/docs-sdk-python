# tag::cloud_connect[]
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.cluster import PasswordAuthenticator
from couchbase.cluster import QueryOptions

# Update this to your cluster
endpoint = "--your-instance--.dp.cloud.couchbase.com"
username = "username"
password = "password"
bucket_name = "bucketname"
cert_path = "path/to/certificate"
# User Input ends here.

# Initialize the Connection
cluster = Cluster("couchbases://{}".format(endpoint), ClusterOptions(
    PasswordAuthenticator(username, password, cert_path=cert_path)))
cb = cluster.bucket(bucket_name)
cb_coll = cb.default_collection()

# Create a SQL++ (formerly N1QL) Primary Index (but ignore if it exists)
cluster.query_indexes().create_primary_index(
    bucket_name, ignore_if_exists=True)

# Store a Document
cb_coll.upsert("u:king_arthur", {
               "name": "Arthur", "email": "kingarthur@couchbase.com", "interests": ["Holy Grail", "African Swallows"]})

# Load the Document and print it
print(cb_coll.get("u:king_arthur").content_as[str])

# Perform a SQL++ (formerly N1QL) Query
row_iter = cluster.query("SELECT cbc.* FROM {} cbc WHERE $1 IN cbc.interests".format(
    bucket_name), QueryOptions(positional_parameters=["African Swallows"]))

# Print each found Row
for row in row_iter.rows():
    print("Found row: {}".format(row))
# end::cloud_connect[]
