
"""
[source,python]
----
"""
#tag::intro[]
from couchbase.cluster import Cluster, ClusterOptions
from couchbase_core.cluster import PasswordAuthenticator

cluster = Cluster('couchbase://localhost', ClusterOptions(PasswordAuthenticator('username', 'password')))
cb = cluster.bucket('bucket-name')
cb_coll = cb.default_collection()
cb_coll.upsert('u:king_arthur',
               {'name': 'Arthur', 'email': 'kingarthur@couchbase.com', 'interests': ['Holy Grail', 'African Swallows']})
# OperationResult<RC=0x0, Key=u'u:king_arthur', CAS=0xb1da029b0000>

print(cb_coll.get('u:king_arthur').content_as[str])
# {u'interests': [u'Holy Grail', u'African Swallows'], u'name': u'Arthur', u'email': u'kingarthur@couchbase.com'}

## The CREATE PRIMARY INDEX step is only needed the first time you run this script
cluster.query('CREATE PRIMARY INDEX ON bucket-name')

from couchbase.cluster import QueryOptions
row_iter = cluster.query('SELECT name FROM bucket-name WHERE $1 IN interests', QueryOptions(positional_parameters=['African Swallows']))
for row in row_iter: print(row)
# {u'name': u'Arthur'}
#end::intro[]
"""
----

== Connecting

To connect to a Couchbase bucket, you must use Couchbase _Role-Based Access Control_ (RBAC).
This is fully described in the section xref:6.0@server:security:security-authorization.adoc[Authorization].
An _authenticator_, containing username and password, should be defined, and then passed to the Cluster constructor.
Following successful authentication, the bucket can be opened.

[source,python]
----
"""
#tag::connecting[]
from couchbase.cluster import Cluster, ClusterOptions
from couchbase_core.cluster import PasswordAuthenticator
cluster = Cluster('couchbase://localhost', ClusterOptions(PasswordAuthenticator('username', 'password')))
bucket = cluster.bucket('bucket-name')
coll = bucket.default_collection()
#end::connecting[]
"""
----

Once defined, the authenticator can be passed to other clusters, as appropriate.

See xref:managing-connections.adoc[Managing Connections Using the Python SDK with Couchbase Server] for more connection options and details about the connection string.

== Document Operations

xref:core-operations.adoc[Document operations], such as storing and retrieving documents, can be done using simple methods on the [.api]`Bucket` class such as [.api]`Bucket.get` and [.api]`Bucket.upsert`.
Simply pass the key (and value, if applicable) to the relevant methods.

[source,python]
----
"""
#tag::docopsget[]
rv = coll.get('document-id')
print(rv.content)
#end::docopsget[]
"""
----

[source,python]
----
"""
#tag::docopsupsert[]
coll.upsert('document-id', {'application': 'data'})
#end::docopsupsert[]
"""----

== N1QL Queries

Couchbase N1QL queries are performed by creating a [.api]`N1QLQuery` object and passing that to the [.api]`Bucket.n1ql_query()` method:

[source,python]
----
"""
#tag::n1ql[]
from couchbase.cluster import QueryOptions

query_result = cluster.query("""SELECT airportname, city, country FROM `travel-sample` """
                             """WHERE type="airport" AND city=$my_city""",
                             QueryOptions(named_parameters={'my_city': "Reno"}))
for row in query_result:
    print(row)
#end::n1ql[]
"""----
"""
