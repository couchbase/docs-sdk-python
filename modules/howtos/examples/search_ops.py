
from couchbase.mutation_state import MutationState
from couchbase.search import (
    SearchOptions, SearchScanConsistency, HighlightStyle, TermFacet)
# tag::search_basic_example[]
from couchbase.cluster import Cluster, ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
import couchbase.search as search


cluster = Cluster.connect(
    "couchbase://localhost",
    ClusterOptions(PasswordAuthenticator("Administrator", "password")))
bucket = cluster.bucket("travel-sample")
collection = bucket.default_collection()

try:
    result = cluster.search_query(
        "travel-sample-index", search.QueryStringQuery("swanky"))

    for row in result.rows():
        print("Found row: {}".format(row))

    print("Reported total rows: {}".format(
        result.metadata().metrics.total_rows))

except CouchbaseException as ex:
    import traceback
    traceback.print_exc()

# end::search_basic_example[]

# tag::search_result[]
result = cluster.search_query(
    "travel-sample-index", search.PrefixQuery("swim"), SearchOptions(fields=["description"]))

for row in result.rows():
    print("Score: {}".format(row.score))
    print("Document Id: {}".format(row.id))

    # print fields included in query:
    print(row.fields)
# end::search_result[]

# tag::limit_and_skip[]
result = cluster.search_query(
    "travel-sample-index", search.TermQuery("downtown"), SearchOptions(limit=4, skip=3))
# end::limit_and_skip[]

# tag::scan_consistency[]
result = cluster.search_query(
    "travel-sample-index", search.TermQuery("downtown"), SearchOptions(scan_consistency=SearchScanConsistency.NOT_BOUNDED))
# end::scan_consistency[]

# tag::ryow[]
new_airline = {
    "callsign": None,
    "country": "United States",
    "iata": "TX",
    "icao": "TX99",
    "id": 123456789,
    "name": "Howdy Airlines",
    "type": "airline"
}

res = collection.upsert(
    "airline_{}".format(new_airline["id"]), new_airline)

ms = MutationState(res)

result = cluster.search_query(
    "travel-sample-index", search.PrefixQuery("howdy"), SearchOptions(consistent_with=ms))
# end::ryow[]

# tag::highlight[]
result = cluster.search_query(
    "travel-sample-index", search.TermQuery("downtown"), SearchOptions(highlight_style=HighlightStyle.Html, highlight_fields=["description", "name"]))
# end::highlight[]

for row in result.rows():
    print("Fragments: {}".format(row.fragments))

# tag::sort[]
result = cluster.search_query(
    "travel-sample-index", search.TermQuery("downtown"), SearchOptions(sort=["_score", "description"]))
# end::sort[]

# tag::facets[]
result = cluster.search_query(
    "travel-sample-index", search.QueryStringQuery("north"), SearchOptions(facets={"types": TermFacet("type", 5)}))
# end::facets[]

result.rows()
print(result.facets()["types"])

# tag::fields[]
result = cluster.search_query(
    "travel-sample-index", search.TermQuery("swanky"), SearchOptions(fields=["name", "description"]))
# end::fields[]

# tag::collections[]
result = cluster.search_query(
    "travel-sample-index", search.TermQuery("downtown"), SearchOptions(collections=["hotel", "airport"]))
# end::collections[]
