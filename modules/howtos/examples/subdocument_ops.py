"""= Sub-Document Operations with the Python SDK
:navtitle: Sub-Doc Operations
:page-topic-type: howto
include::partial$attributes.adoc[]

[abstract]
_Sub-document_ operations can be used to efficiently access _parts_ of documents.
Sub-document operations may be quicker and more network-efficient than _full-document_ operations such as _upsert_, _replace_ and _get_ because they only transmit the accessed sections of the document over the network.
Sub-document operations are also atomic, allowing safe modifications to documents with built-in concurrency control.

== Sub-documents

Starting with Couchbase Server 4.5 you can atomically and efficiently update and retrieve _parts_ of a document.
These parts are called _sub-documents_.
While full-document retrievals retrieve the entire document and full document updates require sending the entire document, sub-document retrievals only retrieve relevant parts of a document and sub-document updates only require sending the updated portions of a document.
You should use sub-document operations when you are modifying only portions of a document, and full-document operations when the contents of a document is to change significantly.

IMPORTANT: The sub-document operations described on this page are for _Key-Value_ requests only: they are not related to sub-document N1QL queries.
(Sub-document N1QL queries are explained in the section xref:n1ql-query.adoc[Querying with N1QL].)

In order to use sub-document operations you need to specify a _path_ indicating the location of the sub-document.
The _path_ follows N1QL syntax (see https://developer.couchbase.com/documentation/server/current/sdk/subdocument-operations.html#story-h2-12[below^], and xref:6.0@server:n1ql:n1ql-intro/queriesandresults.adoc[N1QL Queries and Results]).
Considering the document:

.customer123.json
 [source,json]
 ----
{
    "name": "Douglas Reynholm",
    "email": "douglas@reynholmindustries.com",
    "addresses": {
        "billing": {
            "line1": "123 Any Street",
            "line2": "Anytown",
            "country": "United Kingdom"
        },
        "delivery": {
            "line1": "123 Any Street",
            "line2": "Anytown",
            "country": "United Kingdom"
        }
    },
    "purchases": {
        "complete": [
            339, 976, 442, 666
        ],
        "abandoned": [
            157, 42, 999
        ]
    }
}
 ----

The paths `name`, `addresses.billing.country` and `purchases.complete[0]` are all valid paths.

                                                                                        == Retrieving


The _lookup-in_ operations query the document for certain path(s); these path(s) are then returned.
You have a choice of actually retrieving the document path using the _subdoc-get_ sub-document operation, or simply querying the existence of the path using the _subdoc-exists_ sub-document operation.
The latter saves even more bandwidth by not retrieving the contents of the path if it is not needed.

.Retrieve sub-document value
[source,csharp]
----
"""
from couchbase.collection import CBCollection
import couchbase.subdocument as SD
from couchbase.durability import Durability
collection = CBCollection()
#tag::content_as[]

result = collection.lookup_in("customer123", [SD.get("addresses.delivery.country")])
country = result.content_as[str](0) # "United Kingdom"
#end::content_as[]
"""
----

.Check existence of sub-document path
[source,csharp]
----
"""
#tag::exists[]
result = collection.lookup_in("customer123", [SD.exists("purchases.pending[-1]")])
print("Path exists? {}".format(result.content_as[bool](0)))
"""
# Path exists? false
#end::exists[]
----

Multiple operations can be combined as well:

    .Combine multiple lookup operations
                             [source,csharp]
                             ----
"""
#tag::combine[]
result = collection.lookup_in("customer123", (SD.get("addresses.delivery.country"), SD.exists("purchases.pending[-1]")))

print("{0}", result.content_as[str](0))
print("Path exists? {0}", result.content_as[bool](1))
#end::combine[]
"""
----

== Mutating

Mutation operations modify one or more paths in the document.
    The simplest of these operations is _subdoc-upsert_, which, similar to the fulldoc-level _upsert_, will either modify the value of an existing path or create it if it does not exist:

.Upserting a new sub-document
[source,csharp]
                 ----
"""
#tag::upsert[]
collection.mutate_in("customer123", [SD.upsert("fax", "311-555-0151")])
#end::upsert[]
"""
----

Likewise, the _subdoc-insert_ operation will only add the new value to the path if it does not exist:

.Inserting a sub-document
[source,csharp]
             ----
"""
#tag::insert[]
collection.mutate_in("customer123", [SD.insert("purchases.complete", [42, True, "None"])])

# SubdocPathExistsError
#end::insert[]
"""
----

Dictionary values can also be replaced or removed, and you may combine any number of mutation operations within the same general _mutate-in_ API.
    Here's an example of one which replaces one path and removes another.

        [source,csharp]
        ----
"""
#tag::combine_dict[]
collection.mutate_in("customer123", (SD.remove("addresses.billing"), SD.replace("email", "dougr96@hotmail.com")))
#end::combine_dict[]
"""----

NOTE: `mutateIn` is an _atomic_ operation.
    If any single `ops` fails, then the entire document is left unchanged.

                                                                == Array append and prepend

The _subdoc-array-prepend_ and _subdoc-array-append_ operations are true array prepend and append operations.
    Unlike fulldoc _append_/_prepend_ operations (which simply concatenate bytes to the existing value), _subdoc-array-append_ and _subdoc-array-prepend_ are JSON-aware:

[source,csharp]
----
"""
#tag::arrayappend[]
collection.mutate_in("customer123",  SD.array_append("purchases.complete", 777))

# purchases.complete is now [339, 976, 442, 666, 777]
#end::arrayappend[]
"""
----

[source,csharp]
----
"""
#tag::arrayprepend[]
collection.mutate_in("customer123", [SD.array_prepend("purchases.abandoned", 18)])

# purchases.abandoned is now [18, 157, 49, 999]
#end::arrayprepend[]
"""
----

If your document only needs to contain an array, you do not have to create a top-level object wrapper to contain it.
    Simply initialize the document with an empty array and then use the empty path for subsequent sub-document array operations:

    .Creating and populating an array document
                                      [source,csharp]
                                      ----
"""
#tag::createarray[]
collection.upsert("my_array", [])
collection.mutate_in("my_array", [SD.array_append("", "some element")])

# the document my_array is now ["some element"]
#end::createarray[]
"""
----

If you wish to add multiple values to an array, you may do so by passing multiple values to the _array-append_, _array-prepend_, or _array-insert_ operations.
    Be sure to know the difference between passing a collection of multiple elements (in which case the collection is inserted as a single element in the array, as a sub-array) and passing multiple elements (in which case the elements are appended individually to the array):

.Add multiple elements to an array
                             [source,csharp]
                             ----
"""
#tag::addmulti[]
collection.mutate_in("my_array", [SD.array_append("", "elem1", "elem2", "elem3")])

# the document my_array is now ["some_element", "elem1", "elem2", "elem3"]
#end::addmulti[]
"""
----

.Add single array as element to existing array
                                         [source,csharp]
                                         ----
"""
#tag::addnestedarray[]
collection.mutate_in("my_array",[SD.array_append('', 'elem1', 'elem2', 'elem3')])
# the document my_array is now ["some_element", ["elem1", "elem2", "elem3"]]
#end::addnestedarray[]
"""
----

Note that passing multiple values to a single _array-append_ operation results in greater performance increase and bandwidth savings than simply specifying a single _array-append_ for each element.

        .Adding multiple elements to array (slow)
[source,csharp]
----
"""
#tag::addmultislow[]
collection.mutate_in("my_array", (SD.array_append("", "elem1"),SD.array_append("", "elem2"),SD.array_append("", "elem3")))
#end::addmultislow[]
"""
----

If you wish to create an array if it does not exist and also push elements to it within the same operation you may use the <<subdoc-create-parents,_create-path_>> option:

    [source,csharp]
    ----
"""
#tag::createparentsarray[]
collection.mutate_in("some_doc", [SD.array_append("some.array", "Hello", "World",create_parents=True)])
#end::createparentsarray[]
"""
----

== Arrays as Unique Sets

Limited support also exists for treating arrays like unique sets, using the _subdoc-array-addunique_ command.
This will do a check to determine if the given value exists or not before actually adding the item to the array:

    [source,csharp]
    ----
"""
#tag::arrayaddunique[]
collection.mutate_in("customer123", [SD.array_addunique("purchases.complete", 95)])

# => Success

collection.mutate_in("customer123", [SD.array_addunique("purchases.complete", 95)])

# => SubdocPathExists exception!
#end::arrayaddunique[]
"""
----

Note that currently the _addunique_ will fail with a _Path Mismatch_ error if the array contains JSON _floats_, _objects_, or _arrays_.
The _addunique_ operation will also fail with _Cannot Insert_ if the value to be added is one of those types as well.

Note that the actual position of the new element is undefined, and that the array is not ordered.

== Array insertion

New elements can also be _inserted_ into an array.
While _append_ will place a new item at the _end_ of an array and _prepend_ will place it at the beginning, _insert_ allows an element to be inserted at a specific _position_.
The position is indicated by the last path component, which should be an array index.
For example, to insert `"cruel"` as the second element in the array `["Hello", "world"]`, the code would look like:

    [source,csharp]
    ----
"""
#tag::arrayinsert[]
collection.mutate_in("array", [SD.array_insert("[1]", "cruel")])
#end::arrayinsert[]
"""
----

// for your examples, above, CD: “I feel like somewhere in this we should also just a an example path like "my.path[1]" too, just to show how to use the index with a nested path. I don't think it's necessarily clear.”

Note that the array must already exist and that the index must be valid (i.e.
it must not point to an element which is out of bounds).

== Counters and numeric fields

Counter operations allow the manipulation of a _numeric_ value inside a document.
These operations are logically similar to the _counter_ operation on an entire document:

    [source,csharp]
    ----
"""
#tag::counter1[]
result = collection.mutate_in("customer123", SD.counter("logins", 1))

print(collection.get("customer123").content['logins']) # 1

#end::counter1[]
"""
                                       ----

The _subdoc-counter_ operation performs simple arithmetic against a numeric value, either incrementing or decrementing the existing value.
    The new value is returned.

[source,csharp]
            ----
"""
#tag::counter2[]
collection.upsert("player432", {'gold':1000})

result = collection.mutate_in("player432", SD.counter("gold", -150))

# => player 432 now has 850 gold remaining
#end::counter2[]
"""
----

The existing value for _subdoc-counter_ operations must be within range of a 64 bit signed integer.
If the value does not exist, the _subdoc-counter_ operation will create it (and its parents, if _create-path_ is enabled).

Note that there are several differences between _subdoc-counter_ and the full-document _counter_ operations:

    * Sub-document counters have a range of -9223372036854775807 to 9223372036854775807 (i.e. `Iint64.MinValue` and `Int64.MaxValue), whereas full-document counters have a range of 0 to 18446744073709551615 (`UInt64.MaxValue`)
                                                                                                                                                                                          * Sub-document counter operations protect against overflow and underflow, returning an error if the operation would exceed the range.
                                                                                                                                                                                                                                                                                                                             Full-document counters will use normal C semantics for overflow (in which the overflow value is carried over above 0), and will silently fail on underflow, setting the value to 0 instead.
* Sub-document counter operations can operate on any numeric value within a document, while full-document counter operations require a specially formatted counter document with only the counter value.

== Executing multiple operations

Multiple sub-document operations can be executed at once on the same document, allowing you to retrieve or modify several sub-documents at once.
When multiple operations are submitted within the context of a single _lookup-in_ or _mutate-in_ command, the server will execute all the operations with the same version of the document.

NOTE: Unlike _batched operations_ which is simply a way of sending multiple individual operations efficiently on the network, multiple subdoc operations are formed into a single command packet, which is then executed atomically on the server.
You can submit up to 16 operations at a time.

When submitting multiple _mutation_ operations within a single _mutate-in_ command, those operations are considered to be part of a single transaction: if any of the mutation operations fail, the server will logically roll-back any other mutation operations performed within the _mutate-in_, even if those commands would have been successful had another command not failed.

When submitting multiple _retrieval_ operations within a single _lookup-in_ command, the status of each command does not affect any other command.
This means that it is possible for some retrieval operations to succeed and others to fail.
While their statuses are independent of each other, you should note that operations submitted within a single _lookup-in_ are all executed against the same _version_ of the document.

[#subdoc_create_path]
== Creating parents

Sub-document mutation operations such as _subdoc-upsert_ or _subdoc-insert_ will fail if the _immediate parent_ is not present in the document.
    Consider:

[source,json]
----
{
    "level_0": {
        "level_1": {
            "level_2": {
                "level_3": {
                    "some_field": "some_value"
                }
            }
        }
    }
}
----

Looking at the `some_field` field (which is really `level_0.level_1.level_2.level_3.some_field`), its _immediate_ parent is `level_3`.
    If we were to attempt to insert another field, `level_0.level_1.level_2.level_3.another_field`, it would succeed because the immediate parent is present.
    However if we were to attempt to _subdoc-insert_ to `level_1.level_2.foo.bar` it would fail, because `level_1.level_2.foo` (which would be the immediate parent) does not exist.
    Attempting to perform such an operation would result in a Path Not Found error.

    By default the automatic creation of parents is disabled, as a simple typo in application code can result in a rather confusing document structure.
    Sometimes it is necessary to have the server create the hierarchy however.
    In this case, the _create-path_ option may be used.

                                                  [source,csharp]
                                                  ----
"""
#tag::createparents[]
collection.mutate_in("customer123", [SD.upsert("level_0.level_1.foo.bar.phone",
                                               dict(
                                                   num="311-555-0101",
                                                   ext=16
                                               ), create_parents=True)])
#end::createparents[]
"""
----

== CAS Semantics

Subdoc mostly eliminates the need for tracking the xref:concurrent-mutations-cluster.adoc[CAS] value.
    Subdoc operations are atomic and therefore if two different threads access two different sub-documents then no conflict will arise.
    For example the following two blocks can execute concurrently without any risk of conflict:

[source,csharp]
----
"""
#tag::cas1[]
collection.mutate_in("customer123", [SD.array_append("purchases.complete",cas=999)])
#end::cas1[]
"""
----

[source,csharp]
----
"""
#tag::cas2[]
collection.mutate_in("customer123", [SD.array_append("purchases.abandoned",cas=998)])
#end::cas2[]
"""
== Durability
----

In Couchbase Server 6.5 and up, this is built upon with xref:concept-docs:durability.adoc#synchronous-durability[Synchronous Replication], 
which uses the concept of xref:6.5@server:learn:data/durability.adoc#majority[majority] to indicate the number of configured Data Service nodes to which commitment is required:

[source,python]
----
"""
#tag:new_durability[]
collection.mutate_in("key",[SD.insert("name", "mike")], durability_level=Durability.MAJORITY)
#end:new_durability[]
"""
----

== Error handling

Subdoc operations have their own set of errors.
    When programming with subdoc, be prepared for any of the full-document errors (such as _Document Not Found_) as well as special sub-document errors which are received when certain constraints are not satisfied.
Some of the errors include:

    * *Path does not exist*: When retrieving a path, this means the path does not exist in the document.
    When inserting or upserting a path, this means the _immediate parent_ does not exist.
                                                                                   * *Path already exists*: In the context of an _insert_, it means the given path already exists.
    In the context of _array-add-unique_, it means the given value already exists.
                                                                           * *Path mismatch*: This means the path may exist in the document, but that there is a type conflict between the path in the document and the path in the command.
    Consider the document:
+
[source,json]
----
{ "tags": ["reno", "nevada", "west", "sierra"] }
----
+
The path `tags.sierra` is a mismatch, since `tags` is actually an array, while the path assumes it is a JSON object (dictionary).

* *Document not JSON*: This means you are attempting to modify a binary document using sub-document operations.
* *Invalid path*: This means the path is invalid for the command.
    Certain commands such as _subdoc-array-insert_ expect array elements as their final component, while others such as _subdoc-upsert_ and _subdoc-insert_ expect dictionary (object) keys.

If a Sub-Document command fails a top-level error is reported (_Multi Command Failure_), rather than an individual error code (e.g. _Path Not Found_).
When receiving a top-level error code, you should traverse the results of the command to see which individual code failed.

== Path syntax

Path syntax largely follows N1QL conventions: A path is divided into components, with each component referencing a specific _level_ in a document hierarchy.
Components are separated by dots (`.`) in the case where the element left of the dot is a dictionary, or by brackets (`[n]`) where the element left of the bracket is an array and `n` is the index within the array.

As a special extension, you can indicate the _last element_ of an array by using an index of `-1`, for example to get the last element of the array in the document

[source,json]
----
{"some":{"array":[1,2,3,4,5,6,7,8,9,0]}}
----

Use `some.array[-1]` as the path, which will return the element `0`.

Each path component must conform as a JSON string, as if it were surrounded by quotes, and any character in the path which may invalidate it as a JSON string must be escaped by a backslash (`\`).
In other words, the path component must match exactly the path inside the document itself.
For example:

[source,json]
----
{"literal\"quote": {"array": []}}
----

must be referenced as `literal\"quote.array`.

If the path also has special path characters (i.e.
                                              a dot or brackets) it may be escaped using N1QL escapes.
Considering the document

[source,json]
----
{"literal[]bracket": {"literal.dot": true}}
----

A path such as
\`literal[]bracket`.\`literal.dot`.
You can use double-backticks (pass:c[``]) to reference a literal backtick.

If you need to combine both JSON _and_ path-syntax literals you can do so by escaping the component from any JSON string characters (e.g.
                                                                                                                                     a quote or backslash) and then encapsulating it in backticks (`pass:c[`path`]`).

NOTE: Currently, paths cannot exceed 1024 characters, and cannot be more than 32 levels deep.

== XDCR

XDCR only replicates full documents.
Sub-documents are only replicated as part of the full document.

"""