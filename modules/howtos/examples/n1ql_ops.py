from couchbase_core.mutation_state import  MutationState
from couchbase.cluster import Cluster
cluster=Cluster("localhost")
bucket=cluster.bucket("default")
collection=bucket.default_collection()
#tag::positional[]
result = collection.query(
    "SELECT x.* FROM `default` WHERE x.Type=$1",
    'User')
#end::positional[]

#tag::named[]
result = collection.query(
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
from couchbase_core.n1ql import N1QLQuery
query=N1QLQuery(
    "SELECT x.* FROM `default` WHERE x.Type=$1",
    'User')
query.consistent_with(state)
result = cluster.query(query)
#end::consistency[]

