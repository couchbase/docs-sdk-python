"""
[source,python]
----
"""
# tag::connect[]
from couchbase.cluster import Cluster, ClusterOptions
from couchbase_core.cluster import PasswordAuthenticator
from couchbase.cluster import QueryOptions

# get a reference to our cluster
cluster = Cluster('couchbase://hulk', ClusterOptions(
  PasswordAuthenticator('Administrator', 'password')))
# end::connect[]

# tag::bucket[]
# get a reference to our bucket
cb = cluster.bucket('travel-sample')
# end::bucket[]

# tag::default-collection[]
# get a reference to the default collection
cb_coll = cb.default_collection()
# end::default-collection[]



# tag::upsert-func[]
def upsertDocument(doc):
  print("\nUpsert CAS: ")
  try:
    # key will equal: "airline_8091"
    key = doc["type"] + "_" + str(doc["id"])
    result = cb_coll.upsert(key, doc)
    print(result.cas)
  except Exception as e:
    print(e)
# end::upsert-func[]

# tag::get-func[]
# get document function
def getAirlineByKey(key):
  print("\nGet Result: ")
  try:
    result = cb_coll.get(key)
    print(result.content_as[str])
  except Exception as e:
    print(e)
# end::get-func[]

#tag::lookup-func[]
# query for new document by callsign
def lookupByCallsign(cs):
  print("\nLookup Result: ")
  try:
    sqlQuery = 'SELECT VALUE name FROM `travel-sample` WHERE type = "airline" AND callsign = $1' 
    row_iter = cluster.query(
      sqlQuery, 
      QueryOptions(positional_parameters=[cs]))
    for row in row_iter: print(row)
  except Exception as e:
    print(e)
# end::lookup-func[]



# tag::test-doc[]
airline = {
  "type": "airline",
  "id": 8091,
  "callsign": "CBS",
  "iata": None,
  "icao": None,
  "name": "Couchbase Airways",
}
# end::test-doc[]

# tag::upsert-invoke[]
upsertDocument(airline)
# end::upsert-invoke[]

# tag::get-invoke[]
getAirlineByKey("airline_8091")
#end::get-invoke[]

# tag::lookup-invoke[]
lookupByCallsign("CBS")
# end::lookup-invoke[]