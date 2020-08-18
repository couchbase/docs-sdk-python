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
import acouchbase.cluster
import couchbase.cluster
import couchbase.auth
cluster = acouchbase.cluster.Cluster("couchbase://localhost", couchbase.cluster.ClusterOptions(couchbase.auth.PasswordAuthenticator("user", "password")))
cluster.bucket("travel-sample")

bucket = cluster.bucket("default")
await bucket.on_connect()
collection = bucket.default_collection()
"""
----

"== Asynchronous Programming using `await`

This is the most common and basic ways for consuming Couchbase operations asynchronously via Tasks:

[source,csharp]
----
"""
upsert_result = collection.upsert("doc1", dict(name = "Ted", age = 80))
get_result = collection.get("doc1")
person = getResult.content
"""
----

In this way, every single operation will be fired off on a `System.Threading.Threadpool` thread separately from the main application thread.
Note that in the `UpsertAsync` method above, an exception will be thrown if the operation fails; if it succeeds then the result will be an `IMutationResult` that contains the CAS value for reuse, otherwise it can be ignored.
`GetAsync` returns a `GetResult` if it succeeds, you’ll then have to use `ContentAs` to read the returned value.


== Synchronous Programming using `Task.Result`

The same methods above can also be called synchronously, blocking the calling thread by using the `Result` property:

[source,csharp]
----
"""
upsert_result = collection.upsert("doc1", dict(name = "Ted", age = 80))
get_result=collection.get("doc1")
person = get_result.content_as[str]

"""
----

Another way of doing this is by calling the awaiter explicitly `Task.GetAwaiter().GetResult()`:

[source,csharp]
----
"""
upsert_result = collection.upsert("doc1",dict(Name = "Ted", Age = 80))
getResult = collection.get("doc1")
person = getResult.content()


def tasks():
    """
    ----

    This is a slightly more verbose way of achieving the same goal: calling the `Task` synchronously in a blocking fashion.
    Note that Couchbase suggests using the await keyword and running the Task asynchronously, and not blocking the calling thread!


    == Concurrently executing lots of Tasks using Task.WhenAll

    In certain situations, it may be desirable to execute a large number of Tasks concurrently. The way to batch like this is via the `Task.WhenAll` combinator:

    [source,csharp]
    ----
    tasks = new List<Task<IGetResult>>
    {
        collection.GetAsync("doc1"),
        collection.GetAsync("doc2"),
        collection.GetAsync("doc3"),
        collection.GetAsync("doc4")
    };

    var results = await Task.WhenAll(tasks);
    foreach (var getResult in results)
    {
        var doc = getResult.ContentAs<dynamic>();
    #work with the doc returned
    }
----

In this example we will fetch four documents asynchronously while not blocking the main thread, suspending the state until the results are returned.
Then will loop through and work with each document in a synchronous manner.


== What about Task.Wait, Task.WaitAll

`Task.Wait` and `Task.WaitAll` and other _Wait_ methods will block the main thread synchronously while the Task is run; we do not suggest using either of these methods in most cases.
An example of when you would use one of these methods would be a console app where you do not want the main thread to run through the main method before getting the results back.


== Avoiding DeadLocks

When a Task runs, it suspends the current continuation context, executes the Task, and then attempts to continue back where the continuation context suspended.
In ASP.NET this is the request context; however, in ASP.NET it is not tied to a specific thread and the context only allows one thread to run at a time.
The top level method is blocked by the context and when the continuation context calls back it deadlocks because its already blocked.

The best way to avoid deadlocks such as this, is to avoid blocking on Tasks, which means avoiding any of the _Wait_ methods.
Another handy way of avoiding deadlocks is to not use a synchronization context:

[source,csharp]
----
var result = collection.GetAsync("TheKey").ConfigureAwait(false);
----

This will configure the Task to not use the synchronization context even if it exists.





// rx.net for reactive -- add section later, when appears on Couchbaselabs?

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
----
    """
