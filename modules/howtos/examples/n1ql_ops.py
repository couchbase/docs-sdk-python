from couchbase.mutation_state import  MutationState
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.auth import PasswordAuthenticator
cluster=Cluster.connect("localhost", ClusterOptions(PasswordAuthenticator("user","pass")))
bucket=cluster.bucket("default")
collection=bucket.default_collection()
#tag::positional[]
result = cluster.query(
    "SELECT x.* FROM `default` WHERE x.Type=$1",
    'User')
#end::positional[]

#tag::named[]
result = cluster.query(
    "SELECT x.* FROM `default` WHERE x.Type=$type",
    type='User')
#end::named[]

#tag::iterating[]

result = cluster.query(
    "SELECT x.* FROM `default` WHERE x.Type=$1",
    'User')

# iterate over rows
for row in result:
    # each row is an instance of the query call
    name = row['username']
    age = row['age']
#end::iterating[]

#tag::consistency[]

# create / update document (mutation)
upsert_result = collection.upsert("id",  dict( name = "Mike", type = "User" ))

# create mutation state from mutation results
state = MutationState()
state.add_results(upsert_result)

# use mutation state with query option
result = cluster.query("SELECT x.* FROM `default` WHERE x.Type=$1",
    'User', QueryOptions(consistent_with=state))
#end::consistency[]

