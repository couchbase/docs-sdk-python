"""

= Choosing an API
:navtitle: Choosing an API
:page-topic-type: howto
:page-aliases: ROOT:async-programming,ROOT:batching-operations,multiple-apis,ROOT:asynchronous-frameworks

[abstract]

////
Order by importance / most idiomatic choice

Many Async choice

Gevent
Twisted
Asyncio -- event loop, co-routines, futures

also RQ -- Redis Q...
////
The Couchbase .NET SDK uses the _Task-based Asynchronous Pattern (TAP)_ using types in the System.Threading.Tasks namespace to represent asynchronous operations against the Couchbase Server which can be awaited via the `await` keyword. There is no separate synchronous API, however, all tasks can be run synchronously in a blocking fashion using the `Task.Result` method. Batching may be done with Task.WhenAll.


A couple of points to consider:
All operations are composed of a `Task` or a `Task<IResult>` depending upon whether or not the task return void or a `TResult`.
Tasks are evaluated asynchronously using the familiar `await` keyword, and run in a blocking method by calling the `Task.Result()` method.
If a task is awaited, the method awaiting the task must have the `async` keyword in its signature.
Tasks can be run concurrently using any of the `System.Threading.Tasks` combinators: `Task.Run`, `Task.WhenAll`, `Task.WhenAny`, etc.
More information can be found in Microsoft's documentation here: https://docs.microsoft.com/en-us/dotnet/standard/asynchronous-programming-patterns/consuming-the-task-based-asynchronous-pattern#combinators.

Note: All examples on this page start with initiating a Cluster object and then opening the default Bucket and Collection:

[source,python]
----
"""
#tag::connect_and_open_collection[]
import acouchbase.cluster
import couchbase.cluster
import couchbase.auth
cluster = acouchbase.cluster.Cluster("couchbase://localhost", couchbase.cluster.ClusterOptions(couchbase.auth.PasswordAuthenticator("user", "password")))
cluster.bucket("travel-sample")

bucket = cluster.bucket("default")
await bucket.on_connect()
collection = bucket.default_collection()
#end::connect_and_open_collection[]
"""
----

== Asynchronous Programming using `await`

This is the most common and basic way for consuming Couchbase operations asynchronously via asyncio:

[source,python]
----
"""
#tag::await[]
upsert_result = await collection.upsert("doc1", dict(name="Ted", age=80))
get_result = await collection.get("doc1")
person = get_result.content
#end::await[]
"""
----

Note that in the `upsert` method above, an exception will be thrown if the operation fails; if it succeeds then the result will be an `MutationResult` that contains the CAS value for reuse, otherwise it can be ignored.
`GetAsync` returns a `GetResult` if it succeeds, you’ll then have to use `content` or `content_as` to read the returned value.

////

Possibly TODO: not implemented yet
== Batching

Asynchronous clients inherently batch operations: because the application receives the response at a later stage in the application, batching will be the result of issuing many requests in sequence.

Batching in .NET using TAP is relively simple.
`await Task.WhenAll()` will group together tasks and wait until they are complete before running,
useful where you do not want the main thread to run through the main method before getting the results back.

[source,dotnet]
----
// collection of things that will complete in the future
var tasks = new List<Task>();

// create tasks to be executed concurrently
// NOTE: these tasks have not yet been scheduled
for (var i = 0; i <100; i++)
    {
        var task = collection.GetAsync($"mykey-{i}");
tasks.Add(task);
}

// Waits until all of the tasks have completed
await Task.WhenAll(tasks);

// can iterate task list to get results
foreach (var task in tasks)
{
    var result = tasks.Result;
}
////

----
    """
