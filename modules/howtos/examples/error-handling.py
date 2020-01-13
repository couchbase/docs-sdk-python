"""
== How the SDK Handles Errors [EH1]
== Handling Errors
=== Failing [EH2]
=== Logging [EH3]
=== Retry [EH4]
=== Fallback
== KV
=== Doc does not exist [EH5]
=== Doc already exists
=== Doc too large
=== CAS Mismatch [EH6]
=== Durability ambiguous [EH7]
=== Durability invalid level [EH7(also)]
=== No Cluster replicas configured [EH7(also)]
=== Replicate to / persist to greater than replica count [EH8]
=== Timeout with replicate to / persist to requirements
== Connections...
== Authentication
=== RBAC Roles - permissions on Service / Bucket / etc.
== Additional Resources



Different SDKs offer different approaches to error-handling. Please expand beyond this doc if appropriate for your SDK.

////
This document is deliberately skeletal and incomplete, as it seems that there is little common ground between SDKs.

Save into howtos/error-handling.adoc
////

////
Go Errors page up at https://docs.couchbase.com/go-sdk/2.0/howtos/error-handling.html -- may not be directly comparable to other SDKs.
////

////
Meta: version 1 goes from EH1-EH6
////
"""
from couchbase import Collection, GetResult, KeyNotFoundException, Durability, KeyExistsException, PersistTo, \
    ReplicateTo, TimeoutException
import couchbase.exceptions
from couchbase.collection import Collection
from couchbase.cluster import Cluster
import logging
collection=Cluster().bucket("fred").default_collection()
"""
= Handling Errors
:navtitle: Handling Errors
:page-topic-type: howto
:page-aliases: handling-error-conditions.adoc
:source-language: csharp

[abstract]
How & why
Common errors
Other stuff


Errors are inevitable.
The developer’s job is to be prepared for whatever is likely to come up -- and to try and be prepared for anything that conceivably could come up.
Couchbase gives you a lot of flexibility, but it is recommended that you equip yourself with an understanding of the possibilities.
== How the SDK Handles Errors [EH1]

Couchbase-specific exceptions are all derived from `CouchbaseException` / `CouchbaseError` *DELETE AS APPROPRIATE*.
Errors that cannot be recovered by the SDK will be returned to the application.
These unrecoverable errors are left to the application developer to handle -- this section covers handling many of the common error scenarios.

== Handling Errors
The approach will depend upon the type of error thrown.
Is it transient?
Is it even recoverable?
Below we examine error handling strategies in relation to the Couchbase SDKs, then take a practical walk through some common error scenarios you are likely to have to handle when working with a Couchbase cluster.

=== Failing [EH2]
While most of the time you want more sophisticated error handling strategies, sometimes you just need to fail.
It makes no sense for some errors to be retried, either because they are not transient, or because you already tried everything to make it work and it still keeps failing.
If containment is not able to handle the error, then it needs to propagate up to a parent component that can handle it.

In the asynchronous case, errors are events like any other for your subscribers.
Once an error occurs, your `Subscriber` is notified in the method `onError(Throwable)`, and you can handle it the way you want to. Note that by `Observable` contract, after the `onError` event, no more `onNext` events will happen.

[source,python]
----
"""

Observable
.error(new Exception("I'm failing"))
.subscribe(new Subscriber<Object>() {
@Override
public void onCompleted() {
}

@Override
public void onError(Throwable e) {
System.err.println("Got Error: " + e);
}

@Override
public void onNext(Object o) {
}
});
"""
----

For synchronous programs, every error is converted into an Exception and thrown so that you can use regular `try`/`catch` semantics.

[source,java]
----
"""
try:
Object data = Observable.error(new Exception("I'm failing"))
.toBlocking()
.single();
} catch(Exception ex) {
System.err.println("Got Exception: " + ex);
}
"""
----

If you do not catch the Exception, it will bubble up:

[source,java]
----
Exception in thread "main" java.lang.RuntimeException: java.lang.Exception: I'm failing
at rx.observables.BlockingObservable.blockForSingle(BlockingObservable.java:482)
at rx.observables.BlockingObservable.single(BlockingObservable.java:349)
----
=== Logging [EH3]
It is always important to log errors, but even more so in the case of reactive applications. Because of the event driven nature, stack traces get harder to look at, and caller context is sometimes lost.
"""
# SDK-specific text in each case
# Note that Logging has its own page.


# recommendation of good practice ADMONITION link
"""
=== Retry [EH4]

Transient errors -- such as those caused by resource starvation -- are best tackled with one of the following retry strategies:

Retry immediately.
Retry with a fixed delay.
Retry with a linearly increasing delay.
Retry with an exponentially increasing delay.
Retry with a random delay.

[source,python]
----
"""

#tag::handle_retryable[]
# This an example of error handling for idempotent operations (such as the full-doc op seen here).

def change_email(collection,  # type: Collection
                 maxRetries  # type: int
                 ):
    try:
        result = collection.get("doc_id")  # type: GetResult

        if not result:
            raise couchbase.exceptions.KeyNotFoundException()
        else:
            content = result.content

        content["email"]="john.smith@couchbase.com"

        collection.replace("doc_id", content);
    except couchbase.exceptions.CouchbaseError as err:
        # isRetryable will be true for transient errors, such as a CAS mismatch (indicating
        # another agent concurrently modified the document), or a temporary failure (indicating
        # the server is temporarily unavailable or overloaded).  The operation may or may not
        # have been written, but since it is idempotent we can simply retry it.
        if err.is_retryable:
            if maxRetries > 0:
                logging.info("Retrying operation on retryable err " + err)
            change_email(collection, maxRetries - 1);
        else:
            # Errors can be transient but still exceed our SLA.
            logging.error("Too many attempts, aborting on err " + err)
            raise

        # If the err is not isRetryable, there is perhaps a more permanent or serious error,
        # such as a network failure.
        else:
            logging.error("Aborting operation on err " + err);
            raise


MAX_RETRIES=5
try:
    change_email(collection, MAX_RETRIES)
except RuntimeError as err:
    # What to do here is highly application dependent.  Options could include:
    # - Returning a "please try again later" error back to the end-user (if any)
    # - Logging it for manual human review, and possible follow-up with the end-user (if any)
    logging.error("Failed to change email")
#end::handle_retryable[]

"""
----

=== Fallback

Instead of (or in addition to) retrying, another valid option is falling back to either a different `Observable`, or to a default value.

== Generic Errors (see Errors rfc)
There are some errors which can be surfaced from across all of the SDK services. These include...

=== Temporary Failure
=== Timeout (possibly covered below in connections?)
=== ServiceNotAvailable
=== ServiceNotConfigured
== KV

The KV Service exposes several common errors that can be encountered - both during development, and to be handled by the production app. Here we will cover some of the most common errors.

=== Doc does not exist [EH5]
"""
#tag::KeyNotFoundException[]

try:
    collection.replace("my-key", {})
except KeyNotFoundException:
    # key does not exist
    pass
#end::KeyNotFoundException[]

#tag::KeyExistsException[]
try:
    collection.insert("my-key",{})
except KeyExistsException:
    # key already exists
    pass
#end::KeyExistsException[]
"""
=== Doc too large
RequestTooBigException

=== CAS Mismatch [EH6]
"""
#tag::CASMismatchException[]
try:
    result = collection.get("my-key")
    collection.replace("my-key", {}, cas = result.cas)
except couchbase.exceptions.CASMismatchException:
    # the CAS value has changed
    pass
#end::CASMismatchException[]
"""
=== Durability ambiguous [EH7]
"""
#tag::DurabilitySyncWriteAmbiguousException[]
try:
    collection.upsert("my-key", {}, durability_level=Durability.PERSIST_TO_MAJORITY)
except couchbase.exceptions.DurabilitySyncWriteAmbiguousException:
    # durable write request has not completed, it is unknown whether the request met the durability requirements or not
    pass
#end::DurabilitySyncWriteAmbiguousException[]

"""
=== Durability invalid level [EH7(also)]
"""
#tag::DurabilityInvalidLevelException[]
try:
    collection.upsert("my-key", {}, durability_level=Durability.PERSIST_TO_MAJORITY)
except couchbase.exceptions.DurabilityInvalidLevelException:
    # cluster not able to meet durability requirements
    pass
#end::DurabilityInvalidLevelException[]
"""
=== No Cluster replicas configured [EH7(also)]
"""
#tag::ReplicaNotConfiguredException[]
try:
    collection.upsert("my-key", {}, persist_to=PersistTo.FOUR, ReplicateTo.THREE)
except couchbase.exceptions.ReplicaNotConfiguredException:
    # cluster doesn't have replicas configured
    pass
#end::ReplicaNotConfiguredException[]
"""
=== Replicate to / persist to greater than replica count [EH8]
"""
#tag::DurabilityImpossibleException[]
try:
    collection.upsert("my-key", {}, persist_to=PersistTo.FOUR, replicate_to=ReplicateTo.THREE)
except couchbase.exceptions.DurabilityImpossibleException:
    # cluster not able to meet durability requirements
    pass
#end::DurabilityImpossibleException[]

"""
=== Timeout with replicate to / persist to requirements
"""
#tag::TimeoutException[]
try:
    collection.upsert("my-key", {}, persist_to=PersistTo.FOUR, replicate_to=ReplicateTo.THREE)
except TimeoutException:
    # document may or may not have persisted to specified durability requirements
    pass
#end::TimeoutException[]
"""

== Query and Analytics Errors
N1ql and Analytics either return results or an error. If there is an error then it exposed in the following way(s)...

== Search and View Errors
Unlike N1ql and Analytics, Search and Views can return multiple errors as well as errors and partial results.
// This next bit is going to be highly SDK specific too.
== Connections...
// Network / buckets / Timeouts / …

Networks, remotely-located clusters, and XDCR all offer opportunities for packets to go astray, or resources to go offline or become temporarily unavailable.
As well as the above `Timeout` errors, and those in the next section on authenticating against clusters, there are ??network-related??
The most common scenarios that the developer is likely to encounter when working with Couchbase Clusters are
?????

== Authentication
=== RBAC Roles - permissions on Service / Bucket / etc.

Standard since Couchbase Data Platform 5.0, xref:[Role Based Access Control (RBAC)] gives fine-grained permissions designed to protect the security of and access to data with a range of user roles encompassing different privileges.
xref:6.5@server:learn:security/authorization-overview.adoc[Refer to our Authorization pages] for a fuller understanding.

The developer must match an application’s need for data access with the necessary permissions for access.
SCENARIO??
---> Certificates?

NOTE: If you are using Couchbase Community Edition, the only _roles_ available are xref:link-here[Bucket Full Access, Admin, and Read-only Admin].




== Additional Resources
Errors & Exception handling is an expansive topic.
Here, we have covered examples of the kinds of exception scenarios that you are most likely to face.
More fundamentally, you also need to weigh up xref:concept-docs:failure-considerations.adoc[concepts of durability].

Diagnostic methods are available to check on the xref:health-check.adoc[health if the cluster], and the xref:tracing-from-the-sdk.adoc[health of the network].

Logging methods are dependent upon the platform and SDK used.
We offer xref:collecting-information.adoc[recommendations and practical examples].

We have a xref:ref:exceptions.adoc[listing of error messages], with some pointers to what to do when you encounter them.

"""
