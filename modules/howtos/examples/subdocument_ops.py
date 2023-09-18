from couchbase.durability import (Durability, ServerDurability,
                                  ClientDurability, ReplicateTo, PersistTo)
from couchbase.exceptions import (
    CASMismatchException,
    CouchbaseException,
    DocumentExistsException,
    PathExistsException,
    PathNotFoundException,
    SubdocCantInsertValueException,
    SubdocPathMismatchException)
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
import couchbase.subdocument as SD
from couchbase.options import MutateInOptions

cluster = Cluster(
    "couchbase://your-ip",
    authenticator=PasswordAuthenticator(
        "Administrator",
        "password"))
bucket = cluster.bucket("travel-sample")
collection = bucket.default_collection()

json_doc = {
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

try:
    collection.insert("customer123", json_doc)
except DocumentExistsException:
    collection.remove("customer123")
    collection.insert("customer123", json_doc)

# tag::lookup_in[]
result = collection.lookup_in("customer123",
                              [SD.get("addresses.delivery.country")])
country = result.content_as[str](0)  # "United Kingdom"
# end::lookup_in[]
print(country)

# fixed in v. 3.1.0; prior to 3.1. result.exists(index)
#   would throw an exception if the path did not exist
# tag::lookup_in_exists[]
result = collection.lookup_in(
    "customer123", [
        SD.exists("purchases.pending[-1]")])
print('Path exists: {}.'.format(result.exists(0)))
# Path exists:  False.
# end::lookup_in_exists[]

# NOTE:  result.content_as[bool](1) would return False
#        this is b/c when checking if a path exists
#        no content is returned and None evaluates to False

try:
    print("Path exists {}.".format(result.content_as[bool](0)))
except PathNotFoundException:
    print("Path does not exist")

# tag::lookup_in_multi[]
result = collection.lookup_in(
    "customer123",
    [SD.get("addresses.delivery.country"),
     SD.exists("purchases.complete[-1]")])

print("{0}".format(result.content_as[str](0)))
print("Path exists: {}.".format(result.exists(1)))
# path exists: True.
# end::lookup_in_multi[]

# tag::mutate_in_upsert[]
collection.mutate_in("customer123", [SD.upsert("fax", "311-555-0151"),])
# end::mutate_in_upsert[]

# tag::mutate_in_insert[]
collection.mutate_in(
    "customer123", [SD.insert("purchases.pending", [42, True, "None"]),])

try:
    collection.mutate_in(
        "customer123", [
            SD.insert(
                "purchases.complete",
                [42, True, "None"]),])
except PathExistsException:
    print("Path exists, cannot use insert.")
# end::mutate_in_insert[]

# tag::combine_dict[]
collection.mutate_in(
    "customer123",
    (SD.remove("addresses.billing"),
     SD.replace(
        "email",
        "dougr96@hotmail.com"),))
# end::combine_dict[]

# NOTE:  the mutate_in() operation expects a tuple or list
# tag::array_append[]
collection.mutate_in(
    "customer123", (SD.array_append(
                    "purchases.complete", 777),))

# purchases.complete is now [339, 976, 442, 666, 777]
# end::array_append[]

# tag::array_prepend[]
collection.mutate_in(
    "customer123", [
        SD.array_prepend(
            "purchases.abandoned", 18)])

# purchases.abandoned is now [18, 157, 42, 999]
# end::array_prepend[]

# tag::create_array[]
collection.upsert("my_array", [])
collection.mutate_in("my_array", [SD.array_append("", "some element")])

# the document my_array is now ["some element"]
# end::create_array[]

# tag::add_multi[]
collection.mutate_in(
    "my_array", [
        SD.array_append(
            "", "elem1", "elem2", "elem3")])

# the document my_array is now ["some_element", "elem1", "elem2", "elem3"]
# end::add_multi[]

# tag::add_nested_array[]
collection.mutate_in(
    "my_array", [
        SD.array_append(
            "", ["elem4", "elem5", "elem6"])])

# the document my_array is now ["some_element", "elem1", "elem2", "elem3",
#                                   ["elem4", "elem5", "elem6"]]]
# end::add_nested_array[]

# tag::add_multi_slow[]
collection.mutate_in(
    "my_array", (SD.array_append("", "elem7"),
                 SD.array_append("", "elem8"),
                 SD.array_append("", "elem9")))

# end::add_multi_slow[]

# tag::create_parents_array[]
collection.upsert("some_doc", {})
collection.mutate_in(
    "some_doc", [
        SD.array_prepend(
            "some.array", "Hello", "World", create_parents=True)])
# end::create_parents_array[]

# tag::array_addunique[]
try:
    collection.mutate_in(
        "customer123", [
            SD.array_addunique(
                "purchases.complete", 95)])
    print('Success!')
except PathExistsException:
    print('Path already exists.')

try:
    collection.mutate_in(
        "customer123", [
            SD.array_addunique(
                "purchases.complete", 95)])
    print('Success!')
except PathExistsException:
    print('Path already exists.')
# end::array_addunique[]

# cannot add JSON obj w/ array_addunique
try:
    collection.mutate_in(
        "customer123", [
            SD.array_addunique(
                "purchases.complete", {"new": "object"})])
except SubdocCantInsertValueException:
    print("Cannot add JSON value w/ array_addunique.")


# cannot add JSON obj w/ array_addunique
collection.mutate_in(
    "customer123", [
        SD.upsert(
            "purchases.cancelled", [{"Date": "Some date"}])])

try:
    collection.mutate_in(
        "customer123", [
            SD.array_addunique(
                "purchases.cancelled", 89)])
except SubdocPathMismatchException:
    print("Cannot use array_addunique if array contains JSON objs.")

# tag::array_insert[]
collection.upsert("array", [])
collection.mutate_in("array", [SD.array_append("", "hello", "world")])
collection.mutate_in("array", [SD.array_insert("[1]", "cruel")])
# end::array_insert[]

# exception raised if attempt to insert in out of bounds position
try:
    collection.mutate_in("array", [SD.array_insert("[6]", "!")])
except PathNotFoundException:
    print("Cannot insert to out of bounds index.")

# can insert into nested arrays as long as the path is appropriate
collection.mutate_in("array", [SD.array_append("", ["another", "array"])])
collection.mutate_in("array", [SD.array_insert("[3][2]", "!")])


# tag::counter1[]
result = collection.mutate_in("customer123", (SD.counter("logins", 1),))
num_logins = collection.get("customer123").content_as[dict]["logins"]
print('Number of logins: {}.'.format(num_logins))
# Number of logins: 1.

# end::counter1[]

# tag::counter2[]
collection.upsert("player432", {"gold": 1000})

collection.mutate_in("player432", (SD.counter("gold", -150),))
result = collection.lookup_in("player432", (SD.get("gold"),))
print("{} has {} gold remaining.".format(
    "player432", result.content_as[int](0)))
# player432 has 850 gold remaining.
# end::counter2[]

# tag::create_parents[]
collection.mutate_in("customer123", [SD.upsert("level_0.level_1.foo.bar.phone",
                                               dict(
                                                   num="311-555-0101",
                                                   ext=16
                                               ), create_parents=True)])
# end::create_parents[]

# tag::cas1[]
collection.mutate_in(
    "customer123", [SD.array_append("purchases.complete", 998)])
# end::cas1[]

# tag::cas2[]
collection.mutate_in(
    "customer123", [SD.array_append("purchases.complete", 999)])
# end::cas2[]

try:
    # tag::cas3[]
    collection.mutate_in(
        "customer123", [SD.array_append("purchases.complete", 999)],
        MutateInOptions(cas=1234))
    # end::cas3[]
except (DocumentExistsException, CASMismatchException) as ex:
    # we expect an exception here as the CAS value is chosen
    # for example purposes
    print(ex)

try:
    # tag::obs_durability[]
    collection.mutate_in(
        "key", [SD.insert("username", "dreynholm")],
        MutateInOptions(durability=ClientDurability(
                        ReplicateTo.ONE,
                        PersistTo.ONE)))
    # end::obs_durability[]
except CouchbaseException as ex:
    print('Need to have more than 1 node for durability')
    print(ex)

try:
    # tag::durability[]
    collection.mutate_in(
        "customer123", [SD.insert("username", "dreynholm")],
        MutateInOptions(durability=ServerDurability(
                        Durability.MAJORITY)))
    # end::durability[]
except CouchbaseException as ex:
    print('Need to have more than 1 node for durability')
    print(ex)

