from couchbase.mutation_state import MutationState
from couchbase.search import (SearchScanConsistency,
                              HighlightStyle,
                              TermFacet,
                              TermQuery)
# tag::search_basic_example[]
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, SearchOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
import couchbase.search as search

auth = PasswordAuthenticator('Administrator', 'password')
cluster = Cluster.connect('couchbase://your-ip', ClusterOptions(auth))
bucket = cluster.bucket('travel-sample')
scope = bucket.scope('inventory')
collection = scope.collection('hotel')

try:
    result = cluster.search_query('travel-sample-index',
                                  search.QueryStringQuery('Paris'))

    for row in result.rows():
        print(f'Found row: {row}')

    print(f'Reported total rows: {result.metadata().metrics().total_rows()}')

except CouchbaseException as ex:
    import traceback
    traceback.print_exc()

# end::search_basic_example[]

# tag::search_result[]
result = cluster.search_query('travel-sample-index',
                              search.PrefixQuery('swim'),
                              SearchOptions(fields=['description']))

for row in result.rows():
    print(f'Score: {row.score}')
    print(f'Document Id: {row.id}')

    # print fields included in query:
    print(row.fields)
# end::search_result[]

# tag::limit_and_skip[]
result = cluster.search_query('travel-sample-index',
                              search.TermQuery('swanky'),
                              SearchOptions(limit=4, skip=3))
# end::limit_and_skip[]

# tag::scan_consistency[]
result = cluster.search_query('travel-sample-index',
                              search.TermQuery('swanky'),
                              SearchOptions(scan_consistency=SearchScanConsistency.NOT_BOUNDED))
# end::scan_consistency[]

# tag::ryow[]
res = collection.upsert(f'hotel_example-123456', {'description': 'swanky'})
ms = MutationState(res)
result = cluster.search_query('travel-sample-index',
                              search.QueryStringQuery('swanky'),
                              SearchOptions(consistent_with=ms))
# end::ryow[]

# tag::highlight[]
result = cluster.search_query('travel-sample-index',
                              search.TermQuery('downtown'),
                              SearchOptions(highlight_style=HighlightStyle.Html,
                                            highlight_fields=['description', 'name']))
# end::highlight[]

for row in result.rows():
    print(f'Fragments: {row.fragments}')

# tag::sort[]
result = cluster.search_query('travel-sample-index',
                              search.TermQuery('downtown'),
                              SearchOptions(sort=['_score', 'description']))
# end::sort[]

# tag::facets[]
facet_name = 'activity'
facet = TermFacet('activity')
query = TermQuery('home')
q_res = cluster.search_query('travel-sample-index',
                            query,
                            SearchOptions(limit=10, facets={facet_name: facet}))

for row in q_res.rows():
    print(f'Found row: {row}')

print(f'facets: {q_res.facets()}')
# end::facets[]

# tag::fields[]
result = cluster.search_query('travel-sample-index',
                              search.TermQuery('swanky'),
                              SearchOptions(fields=['name', 'description']))
# end::fields[]

# tag::collections[]
result = cluster.search_query('travel-sample-index',
                              search.QueryStringQuery('San Francisco'),
                              SearchOptions(collections=['landmark', 'airport']))
# end::collections[]

# this should come from an external source, such as an embeddings API
query_vector = []
another_query_vector = []

# tag::vector_search_single[]
# NOTE: new imports needed for vector search
from couchbase.vector_search import VectorQuery, VectorSearch

vector_search = VectorSearch.from_vector_query(VectorQuery('vector_field',
                                                           query_vector))
request = search.SearchRequest.create(vector_search)
result = scope.search('vector-index', request)
# end::vector_search_single[]

# tag::vector_search_multi[]
request = search.SearchRequest.create(VectorSearch([
    VectorQuery.create('vector_field',
                       query_vector,
                       num_candidates=2,
                       boost=0.3),
    VectorQuery.create('vector_field',
                       another_query_vector,
                       num_candidates=5,
                       boost=0.7)
]))
result = scope.search('vector-index', request)
# end::vector_search_multi[]

# tag::vector_search_combo[]
request = (search.SearchRequest.create(search.MatchAllQuery())
           .with_vector_search(VectorSearch.from_vector_query(VectorQuery('vector_field',
                                                                          query_vector))))
result = scope.search('vector-and-fts-index', request)
# end::vector_search_combo[]

# tag::search_query_search[]
request = search.SearchRequest.create(search.MatchAllQuery())
result = scope.search('travel-sample-index', request)
# end::search_query_search[]