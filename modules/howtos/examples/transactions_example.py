import sys
import traceback
from datetime import timedelta
from typing import TYPE_CHECKING

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.durability import DurabilityLevel, ServerDurability
from couchbase.exceptions import (DocumentNotFoundException,
                                  TransactionCommitAmbiguous,
                                  TransactionFailed)
from couchbase.n1ql import QueryProfile
from couchbase.options import (ClusterOptions, ClusterTimeoutOptions,
                               TransactionConfig, TransactionQueryOptions)

if TYPE_CHECKING:
    from couchbase.transactions import AttemptContext


def main():
    # tag::config[]
    opts = ClusterOptions(authenticator=PasswordAuthenticator("Administrator", "password"),
                          transaction_config=TransactionConfig(
                              durability=ServerDurability(DurabilityLevel.PERSIST_TO_MAJORITY))
                          )

    cluster = Cluster.connect('couchbase://localhost', opts)
    # end::config[]

    test_doc = "foo"

    # tag::ts-bucket[]
    # get a reference to our bucket
    bucket = cluster.bucket("travel-sample")
    # end::ts-bucket[]

    # tag::ts-collection[]
    # get a reference to our collection
    collection = bucket.scope("inventory").collection("airline")
    # end::ts-collection[]

    # tag::ts-default-collection[]
    # get a reference to the default collection, required for older Couchbase server versions
    collection_default = bucket.default_collection()
    # tag::ts-default-collection[]

    # Set up for what we'll do below
    remove_or_warn(collection, 'doc-a')
    remove_or_warn(collection, 'doc-b')
    remove_or_warn(collection, 'doc-c')
    remove_or_warn(collection, test_doc)
    remove_or_warn(collection, 'docId')

    # await collection.upsert("doc-a", {})
    collection.upsert('doc-b', {})
    collection.upsert('doc-c', {})
    collection.upsert('doc-id', {})
    collection.upsert('a-doc', {})

    def txn_insert(ctx):
        ctx.insert(collection, test_doc, 'hello')

    try:
        cluster.transactions.run(txn_insert)
    except TransactionFailed as ex:
        print(f'Transaction did not reach commit point.  Error: {ex}')
    except TransactionCommitAmbiguous as ex:
        print(f'Transaction possibly committed.  Error: {ex}')

    # tag::create[]
    def txn_logic_ex(ctx  # type: AttemptContext
                     ):
        """
        … Your transaction logic here …
        """

    try:
        """
        'txn_logic_ex' is a Python closure that takes an AttemptContext. The
        AttemptContext permits getting, inserting, removing and replacing documents,
        performing SQL++ (N1QL) queries, etc.

        Committing is implicit at the end of the closure.
        """
        cluster.transactions.run(txn_logic_ex)
    except TransactionFailed as ex:
        print(f'Transaction did not reach commit point.  Error: {ex}')
    except TransactionCommitAmbiguous as ex:
        print(f'Transaction possibly committed.  Error: {ex}')
    # end::create[]

    # tag::examples[]
    inventory = cluster.bucket("travel-sample").scope("inventory")

    def txn_example(ctx):
        # insert doc
        ctx.insert(collection, 'doc-a', {})

        # get a doc
        doc_a = ctx.get(collection, 'doc-a')

        # replace a doc
        doc_b = ctx.get(collection, 'doc-b')
        content = doc_b.content_as[dict]
        content['transactions'] = 'are awesome!'
        ctx.replace(doc_b, content)

        # remove a doc
        doc_c = ctx.get(collection, 'doc-c')
        ctx.remove(doc_c)

        # tag::scope-example[]
        # Added the above tag (scope-example) to ignore this section in the docs for now.
        # Once the below TODO is addressed we can remove the tag completely.
        # SQL++ (N1QL) query
        # @TODO:  clean up txns query options, scope, pos args and named args won't work
        # query_str = 'SELECT * FROM hotel WHERE country = $1 LIMIT 2'
        # res = ctx.query(query_str,
        #         TransactionQueryOptions(scope=inventory,
        #                                 positional_args = ['United Kingdom']))
        # end::scope-example[]
        query_str = 'SELECT * FROM `travel-sample`.inventory.hotel WHERE country = "United Kingdom" LIMIT 2;'
        res = ctx.query(query_str)
        rows = [r for r in res.rows()]

        query_str = 'UPDATE `travel-sample`.inventory.route SET airlineid = "airline_137" WHERE airline = "AF"'
        res = ctx.query(query_str)
        rows = [r for r in res.rows()]

    try:
        cluster.transactions.run(txn_example)
    except TransactionFailed as ex:
        print(f'Transaction did not reach commit point.  Error: {ex}')
    except TransactionCommitAmbiguous as ex:
        print(f'Transaction possibly committed.  Error: {ex}')
    # end::examples[]

    # execute other examples
    try:
        print('transaction - get')
        get(cluster, collection, 'doc-a')
        # be sure to use a new key here...
        print('transaction - get w/ read own writes')
        get_read_own_writes(cluster, collection,
                            'doc-id2', {'some': 'content'})
        print('transaction - replace')
        replace(cluster, collection, 'doc-id')
        print('transaction - remove')
        remove(cluster, collection, 'doc-id')
        print('transaction - insert')
        insert(cluster, collection, 'doc-id', {'some': 'content'})
        print("transaction - query_examples")
        query_examples(cluster)
        print("transaction - create_simple")
        create_simple(cluster, collection)
    except TransactionFailed as ex:
        print(f'Txn did not reach commit point.  Error: {ex}')
    except TransactionCommitAmbiguous as ex:
        print(f'Txn possibly committed.  Error: {ex}')


def get_cluster():
    opts = ClusterOptions(authenticator=PasswordAuthenticator("Administrator", "password"),
                          transaction_config=TransactionConfig(
        durability=ServerDurability(DurabilityLevel.PERSIST_TO_MAJORITY)))

    example_cluster = Cluster.connect('couchbase://localhost', opts)
    return example_cluster


def get_collection():
    example_collection = (get_cluster()).bucket(
        "travel-sample").scope("inventory").collection("airline")
    return example_collection


def get_scope():
    inventory_scope = (get_cluster()).bucket(
        "travel-sample").scope("inventory")
    return inventory_scope


def create_simple(cluster, collection):
    # tag::create-simple[]
    def txn_logic(ctx):
        ctx.insert(collection, 'doc1', {'hello': 'world'})

        doc = ctx.get(collection, 'doc1')
        ctx.replace(doc, {'foo': 'bar'})

    cluster.transactions.run(txn_logic)
    # end::create-simple[]


def replace(cluster, collection, key):
    # tag::replace[]
    def txn_logic(ctx):
        doc = ctx.get(collection, key)
        content = doc.content_as[dict]
        content['transactions'] = 'are awesome!'
        ctx.replace(doc, content)

    cluster.transactions.run(txn_logic)
    # end::replace[]


def remove(cluster, collection, key):
    # tag::remove[]
    def txn_logic(ctx):
        doc = ctx.get(collection, key)
        ctx.remove(doc)

    cluster.transactions.run(txn_logic)
    # end::remove[]


def insert(cluster, collection, key, content):
    # tag::insert[]
    def txn_logic(ctx):
        ctx.insert(collection, key, content)

    cluster.transactions.run(txn_logic)
    # end::insert[]


def get(cluster, collection, key):
    # tag::get[]
    def txn_logic(ctx):
        doc = ctx.get(collection, key)
        doc_content = doc.content_as[dict]

    cluster.transactions.run(txn_logic)
    # end::get[]


def get_read_own_writes(cluster, collection, key, content):
    # tag::get_read_own_writes[]
    def txn_logic(ctx):
        ctx.insert(collection, key, content)
        doc = ctx.get(collection, key)
        doc_content = doc.content_as[dict]

    cluster.transactions.run(txn_logic)
    # end::get_read_own_writes[]


def query_examples(cluster):
    # tag::query_examples_select[]
    def txn_select(ctx):
        query_str = 'SELECT * FROM `travel-sample`.inventory.hotel WHERE country = "United Kingdom" LIMIT 2;'
        res = ctx.query(query_str)
        rows = [r for r in res.rows()]

    cluster.transactions.run(txn_select)
    # end::query_examples_select[]

    # @TODO: Ensure that using Scope works, currently this throws an error:
    # Error: TransactionFailed{<message=AttributeError("'Scope' object has no attribute 'bucket'")>}
    # tag::query_examples_select_scope[]
    # def txn_select_scope(ctx):
    #     query_str = 'SELECT * FROM hotel WHERE country = "United Kingdom"'
    #     inventory_scope = get_scope()
    #     res = ctx.query(query_str, TransactionQueryOptions(
    #         scope=inventory_scope)
    #     )
    #     rows = [r for r in res.rows()]

    # cluster.transactions.run(txn_select_scope)
    # end::query_examples_select_scope[]

    # @TODO: Add a check to see if the mutation has gone through (not sure how to do this in python)
    # @TODO: Also, ensure that using Scope works, currently this throws an error:
    # Error: TransactionFailed{<message=AttributeError("'Scope' object has no attribute 'bucket'")>}
    # tag::query_examples_update[]
    # def txn_update(ctx):
    #     inventory_scope = get_scope()
    #     query_str = 'UPDATE hotel SET price = 99.99 WHERE url LIKE "http://marriot%" AND country = "United States"'
    #     res = ctx.query(query_str, TransactionQueryOptions(
    #         scope=inventory_scope)
    #     )

    # cluster.transactions.run(txn_update)
    # end::query_examples_update[]

    # tag::query_examples_complex[]
    def txn_complex(ctx):
        # find all hotels of the chain
        res = ctx.query(
            'SELECT reviews FROM `travel-sample`.inventory.hotel WHERE url = "http://marriot%" AND country = "United States"')

        # This function (not provided here) will use a trained machine learning model to provide a
        # suitable price based on recent customer reviews.
        updated_price = price_from_recent_reviews(res)

        # Set the price of all hotels in the chain
        query_str = f'UPDATE `travel-sample`.inventory.hotel SET price = {updated_price} WHERE url LIKE "http://marriot%" AND country = "United States"'
        ctx.query(query_str)

    cluster.transactions.run(txn_complex)
    # end::query_examples_complex[]


def query_insert(cluster):
    # tag::query_insert[]
    def txn_logic(ctx):
        ctx.query(
            "INSERT INTO `travel-sample` VALUES ('doc', {'hello':'world'})")  # <1>
        query_str = "SELECT hello FROM `travel-sample` WHERE META().id = 'doc'"  # <2>
        res = ctx.query(query_str)

    cluster.transactions.run(txn_logic)
    # end::query_insert[]


def query_ryow(cluster):
    # tag::query_ryow[]
    def txn_logic(ctx):
        collection = cluster.defaultCollection()
        ctx.insert(collection, 'doc-greeting',
                   {'greeting': 'hello world'})  # <1>
        query_str = "SELECT greeting FROM `travel-sample` WHERE META().id = 'doc-greeting'"  # <2>
        res = ctx.query(query_str)

    cluster.transactions.run(txn_logic)
    # end::query_ryow[]


def query_options(cluster):
    # tag::query_options[]
    def txn_logic(ctx):
        res = ctx.query(
            "INSERT INTO `travel-sample` VALUES ('doc-abc', {'hello':'world'})",
            TransactionQueryOptions(
                profile=QueryProfile.TIMINGS
            )
        )

    cluster.transactions.run(txn_logic)
    # end::query_options[]


# @TODO: Verify this is the correct way to perform a single query transaction.
# Currently doesn't seem any different than a normal transaction.
# For example in Java, we would do: inventory.query(bulkLoadStatement, QueryOptions.queryOptions().asTransaction());
def query_single(cluster):
    # tag::query_single[]
    bulk_load_statement = ""  # a bulk-loading SQL++ (N1QL) statement not provided here

    def txn_logic(ctx):
        ctx.query(bulk_load_statement)

    try:
        cluster.transactions.run(txn_logic)
    except TransactionFailed as ex:
        print(f'Transaction did not reach commit point.  Error: {ex}')
    except TransactionCommitAmbiguous as ex:
        print(f'Transaction possibly committed.  Error: {ex}')
    # end::query_single[]

# can't do as there are no query options


def query_single_scoped(cluster):
    bulkLoadStatement = ""  # your statement here

    # tag::query_single_scoped[]
    travelSample = cluster.bucket("travel-sample")
    inventory = travelSample.scope("inventory")
    # end::query_single_scoped[]


def query_single_configured(cluster, collection):
    # tag::full[]
    def player_hits_monster(damage, player_id, monster_id, cluster, collection):
        try:
            def txn_logic(ctx):
                monster_doc = (ctx.get(collection, monster_id)
                               ).content_as[dict]
                player_doc = (ctx.get(collection, player_id)).content_as[dict]

                monster_hit_points = monster_doc["hitpoints"]
                monster_new_hitpoints = monster_hit_points - damage

                if monster_new_hitpoints <= 0:
                    # Monster is killed. The remove is just for demoing, and a more realistic
                    # example would set a "dead" flag or similar.
                    ctx.remove(monster_doc)

                    # The player earns experience for killing the monster
                    experience_for_killing_monster = monster_doc["experience_when_killed"]
                    player_experience = player_doc["experience"]
                    player_new_experience = player_experience + experience_for_killing_monster
                    player_new_level = calculate_level_for_experience(
                        player_new_experience)

                    player_content = player_doc.copy()

                    player_content["experience"] = player_new_experience
                    player_content["level"] = player_new_level

                    ctx.replace(player_doc, player_content)
            cluster.transactions.query(txn_logic)
        except TransactionFailed as ex:
            print(f'Transaction did not reach commit point.  Error: {ex}')
            # The operation failed. Both the monster and the player will be untouched.
            #
            # Situations that can cause this would include either the monster
            # or player not existing (as get is used), or a persistent
            # failure to be able to commit the transaction, for example on
            # prolonged node failure.
        except TransactionCommitAmbiguous as ex:
            print(f'Transaction possibly committed.  Error: {ex}')
            # Indicates the state of a transaction ended as ambiguous and may or
            # may not have committed successfully.
            #
            # Situations that may cause this would include a network or node failure
            # after the transactions operations completed and committed, but before the
            # commit result was returned to the client.
    # end::full[]


def rollback(cluster, collection):
    cost_of_item = 10

    # tag::rollback[]
    def txn_logic(ctx):
        customer = ctx.get(collection, "customer-name")

        if customer.content_as[dict]["balance"] < cost_of_item:
            raise Exception(
                "Transaction failed, customer does not have enough funds.")

        # else continue transaction
    cluster.transactions.run(txn_logic)
    # end::rollback[]


class InsufficientBalanceException(Exception):
    pass


def rollback_cause(cluster, collection):
    cost_of_item = 10

    # tag::rollback_cause[]
    try:
        def txn_logic(ctx):
            customer = ctx.get(collection, "customer-name")

            if customer.content_as[dict]["balance"] < cost_of_item:
                raise InsufficientBalanceException()

            # else continue transaction
        cluster.transactions.run(txn_logic)
    except TransactionCommitAmbiguous:
        # This exception can only be thrown at the commit point, after the
        # BalanceInsufficient logic has been passed, so there is no need to
        # check the cause property here.
        pass
    except InsufficientBalanceException as e:
        raise InsufficientBalanceException("user had Insufficient balance", e)
    # end::rollback_cause[]


def complete_error_handling(cluster, collection):
    # tag::complete_error_handling[]
    try:
        def txn_logic(ctx):
            # ... transactional code here ...
            pass
        result = cluster.transactions.run(txn_logic)
        if not result.unstaging_complete:
            # In rare cases, the application may require the commit to have completed.
            # (Recall that the asynchronous cleanup process is still working to complete the commit.)
            # The next step is application-dependent.
            print("do something...")
    except TransactionCommitAmbiguous as ex:
        # The transaction may or may not have reached commit point
        print(
            f'Transaction returned TransactionCommitAmbiguous and may have succeeded.  Error: {ex}')
    except TransactionFailed as ex:
        # The transaction definitely did not reach commit point
        print(f'Transaction failed with TransactionFailed.  Error: {ex}')
    # end::complete_error_handling[]


def remove_or_warn(collection, key):
    try:
        collection.remove(key)
    except DocumentNotFoundException:
        pass  # this is okay
    except Exception:
        exc_info = sys.exc_info()
        print(f'Failed remove {key}.  Exception: {exc_info[1]}')


def price_from_recent_reviews(qr):
    # this would call a trained ML model to get the best price
    return 99.98


def calculate_level_for_experience(player_new_experience):
    raise Exception("Function not implemeted")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        exc_info = sys.exc_info()
        tb = ''.join(traceback.format_tb(exc_info[2]))
        print(f'Exception info: {exc_info[1]}\nTraceback:\n{tb}')
