from couchbase_core.mutation_state import  MutationState
from couchbase.cluster import Cluster
cluster=Cluster("localhost")
bucket=cluster.bucket("default")
collection=bucket.default_collection()
"""= N1QL Queries from the SDK
:navtitle: N1QL from the SDK
:page-topic-type: howto
:page-aliases: n1ql-query

[abstract]
You can query for documents in Couchbase using the N1QL query language, a language based on SQL, but designed for structured and flexible JSON documents.
Querying can solve typical programming tasks such as finding a user profile by email address, facebook login, or user ID.

include::partial$alpha-warning.adoc[]

Our query service uses N1QL, which will be fairly familiar to anyone who's used any dialect of SQL.
xref:#additional-resources[Further resources] for learning about N1QL are listed at the bottom of the page.
Before you get started you may wish to checkout the xref:6.5@server:n1ql:n1ql-language-reference/index.adoc[N1QL intro page], or just dive in with a query against our travel sample data set.
In this case, the one thing that you need to know is that in order to make a Bucket queryable, it must have at least one index defined.
You can define a _primary_ index on a bucket.
When a primary index is defined you can issue non-covered queries on the bucket as well.

Use
xref:6.5@server::tools/cbq-shell.html[cbq], our interactive Query shell.
Open it, and enter the following:

[source,n1ql]
----
CREATE PRIMARY INDEX ON `travel-sample`
----

or replace _travel-sample_ with a different Bucket name to build an index on a different dataset.

NOTE: The default installation places cbq in `/opt/couchbase/bin/` on Linux, `/Applications/Couchbase Server.app/Contents/Resources/couchbase-core/bin/cbq` on OS X, and `C:\Program Files\Couchbase\Server\bin\cbq.exe` on Microsoft Windows.

// TODO: improving this and/or adding server/6.0/tools/query-workbench.html


== Queries & Placeholders

Placeholders allow you to specify variable constraints for an otherwise constant query.
There are two variants of placeholders: postional and named parameters.
Positional parameters use an ordinal placeholder for substitution and named parameters use variables.
A named or positional parameter is a placeholder for a value in the WHERE, LIMIT or OFFSET clause of a query.
Note that both parameters and options are optional.

.Positional parameter example:
[source,python]
----
"""
#tag::positional[]
result = collection.query(
    "SELECT x.* FROM `default` WHERE x.Type=$1",
    'User')
#end::positional[]

"""
----

.Named parameter example:
[source,python]
----
"""
#tag::named[]
result = collection.query(
    "SELECT x.* FROM `default` WHERE x.Type=$type",
    type='User')
#end::named[]
"""
----

The complete code for this page's example can be found at xref:[??]



== Handling Results

In most cases your query will return more than one result, and you may be looking to iterate over those results:

[source,python]
----
"""
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
"""----

== Scan Consistency


Setting a staleness parameter for queries, with `scan_consistency`, enables a tradeoff between latency and (eventual) consistency.

* A N1QL query using the default *Not Bounded* Scan Consistency will not wait for any indexes to finish updating before running the query and returning results, meaning that results are returned quickly, but the query will not return any documents that are yet to be indexed.

* With Scan Consistency set to *RequestPlus*, all document changes and index updates are processed before the query is run.
Select this when consistency is always more important than performance.

* For a middle ground, *AtPlus* is a "read your own write" (RYOW) option, which means it just waits for the new documents that you specify to be indexed, rather than an entire index of multiple documents.
// See the xref:scan-consistency-examples.adoc[examples] for how to use *AtPlus* for the best performance balance for many circumstances.

.ScanConsisteny (RYOW)
[source,python]
----
"""
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

"""
----

== Streaming Large Result Sets

By default the Python SDK will stream the result set from the server, where the client will start a persistent connection with the server and only read the header until the Rows are enumerated; then, each row or JSON object will be de-serialized one at a time.

This decreases pressure on Garbage Collection and helps to prevent Out Of Memory errors.

== Additional Resources

NOTE: N1QL is not the only query option in Couchbase.
Be sure to check that xref:concept-docs:http-services.adoc[your use case fits your selection of query service].

* For a deeper dive into N1QL from the SDK, refer to our xref:concept-docs:n1ql-query.adoc[N1QL SDK concept doc].
* The xref:6.5@server:n1ql:n1ql-language-reference/index.adoc[Server doc N1QL intro] introduces a complete guide to the N1QL language, including all of the latest additions.
* The http://query.pub.couchbase.com/tutorial/#1[N1QL interactive tutorial] is a good introduction to the basics of N1QL use.
* For scaling up queries, be sure to xref:6.5@server:n1ql:n1ql-language-reference/index.adoc[read up on Indexes].
* N1QL is for operational queries; for analytical workloads, read more on xref:concept-docs:http-services.adoc#Long-Running-Queries-&-Big-Data[when to choose CBAS], our implementation of SQL++.
"""
