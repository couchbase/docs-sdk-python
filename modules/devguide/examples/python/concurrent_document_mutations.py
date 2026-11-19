# tag::imports[]
from datetime import timedelta

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.exceptions import CasMismatchException, DocumentLockedException
from couchbase.options import ClusterOptions, ReplaceOptions
# end::imports[]

cluster = Cluster.connect(
    'couchbase://your-ip',
    ClusterOptions(PasswordAuthenticator('Administrator', 'password')))
collection = cluster.bucket('travel-sample').default_collection()


def add_field1_without_cas(collection):
    # tag::demo_thread_1[]
    result = collection.get('docid')
    new_doc = result.content_as[dict]
    new_doc['field1'] = 'value1'
    collection.replace('docid', new_doc)
    # end::demo_thread_1[]


def add_field2_without_cas(collection):
    # tag::demo_thread_2[]
    result = collection.get('docid')
    new_doc = result.content_as[dict]
    new_doc['field2'] = 'value2'
    collection.replace('docid', new_doc)
    # end::demo_thread_2[]


def add_field1_with_cas(collection):
    # tag::cas_thread_1[]
    result = collection.get('docid')
    new_doc = result.content_as[dict]
    new_doc['field1'] = 'value1'
    collection.replace('docid', new_doc,
                       ReplaceOptions(cas=result.cas))
    # end::cas_thread_1[]


def add_field2_with_cas(collection):
    # tag::cas_thread_2[]
    result = collection.get('docid')
    new_doc = result.content_as[dict]
    new_doc['field2'] = 'value2'
    collection.replace('docid', new_doc,
                       ReplaceOptions(cas=result.cas))
    # end::cas_thread_2[]


# tag::increment_visit_count[]
def increment_visit_count(collection, user_id):
    for _ in range(10):
        # Get the current document contents
        res = collection.get(user_id)

        # Increment the visit count
        user_doc = res.content_as[dict]
        user_doc['visitCount'] += 1

        try:
            # Attempt to replace the document using CAS
            return collection.replace(user_id, user_doc, ReplaceOptions(cas=res.cas))
        except (CasMismatchException, DocumentLockedException):
            # if doc is locked, we get DocumentLockedException
            # if doc was changed between the get and the replace, we get CasMismatchException
            continue
# end::increment_visit_count[]


def lock_and_replace(collection):
    # tag::locking[]
    # get doc, lock for 10 seconds
    get_res = collection.get_and_lock('key', timedelta(seconds=10))

    locked_cas = get_res.cas

    # an example of simply unlocking the document:
    # collection.unlock('key', locked_cas)

    # this should raise an exception
    try:
        collection.replace('key', 'new value')
    except DocumentLockedException:
        print('this is why we lock')

    # this will also fail as well, since a get while locked
    # will not return a valid CAS.
    try:
        bad_cas = collection.get('key').cas
        collection.replace('key', 'new value', ReplaceOptions(cas=bad_cas))
    except DocumentLockedException:
        print('this is also why we lock')

    # this will succeed
    collection.replace('key', 'new value', ReplaceOptions(cas=locked_cas))
    # end::locking[]


collection.upsert('docid', {'a_field': 'a_value'})
add_field1_without_cas(collection)
add_field2_without_cas(collection)
# tag::demo_result[]
print(collection.get('docid').content_as[dict])
# end::demo_result[]

collection.upsert('docid', {'a_field': 'a_value'})
add_field1_with_cas(collection)
add_field2_with_cas(collection)

collection.upsert('user::1', {'visitCount': 0})
increment_visit_count(collection, 'user::1')

collection.upsert('key', 'value')
lock_and_replace(collection)
