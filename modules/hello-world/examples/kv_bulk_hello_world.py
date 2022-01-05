from couchbase.cluster import Cluster, PasswordAuthenticator

cluster = Cluster("couchbase://localhost",
                  authenticator=PasswordAuthenticator("Administrator", "password"))
bucket = cluster.bucket("travel-sample")
users_collection = bucket.scope("tenant_agent_00").collection("users")

# tag::kv-users[]
documents = {
    "user_111": {"id": "user_111", "email": "tom_the_cat@gmail.com"},
    "user_222": {"id": "user_222", "email": "jerry_mouse@gmail.com"},
    "user_333": {"id": "user_333", "email": "mickey_mouse@gmail.com"}
}
# end::kv-users[]

print("[kv-bulk-insert]")
# tag::kv-bulk-insert[]
# Insert some documents in the users collection.
insert_results = users_collection.insert_multi(documents)

# Print each document's CAS metadata to the console.
for key in documents:
    print("Inserted Document:", key)
    print("CAS:", insert_results[key].cas)
# end::kv-bulk-insert[]

print("[kv-bulk-upsert]")
# tag::kv-bulk-upsert[]
# Upsert some documents in the users collection.
upsert_results = users_collection.upsert_multi(documents)

# Print each document's CAS metadata to the console.
for key in documents:
    print("Upserted Document:", key)
    print("CAS:", upsert_results[key].cas)
# end::kv-bulk-upsert[]

print("[kv-bulk-get]")
# tag::kv-bulk-get[]
# Get some documents from the users collection.
get_results = users_collection.get_multi(documents.keys())

# Print each document's CAS metadata to the console.
for key in documents:
    print("Fetched Document:", key)
    print("CAS:", get_results[key].cas)
# end::kv-bulk-get[]

print("[kv-bulk-remove]")
# tag::kv-bulk-remove[]
# Remove some documents from the users collection.
remove_results = users_collection.remove_multi(documents.keys())

# Print each document's CAS metadata to the console.
for key in documents:
    print("Removed Document:", key)
    print("CAS:", remove_results[key].cas)
# end::kv-bulk-remove[]
