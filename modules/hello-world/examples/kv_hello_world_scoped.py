from datetime import datetime, timedelta

from couchbase.cluster import Cluster, PasswordAuthenticator
from couchbase.collection import GetOptions, InsertOptions, ReplaceOptions
from couchbase_core import subdocument

cluster = Cluster("couchbase://localhost",
                  authenticator=PasswordAuthenticator("Administrator", "password"))
bucket = cluster.bucket("travel-sample")
hotel_collection = bucket.scope("inventory").collection("hotel")


def insert():
    print("[kv-insert]")
    # tag::kv-insert[]
    # Create a document object.
    document = {
        "id": 123,
        "name": "Medway Youth Hostel",
        "address": "Capstone Road, ME7 3JE",
        "url": "http://www.yha.org.uk",
        "geo": {
            "lat": 51.35785,
            "lon": 0.55818,
            "accuracy": "RANGE_INTERPOLATED",
        },
        "country": "United Kingdom",
        "city": "Medway",
        "state": None,
        "reviews": [
            {
                "content": "This was our 2nd trip here and we enjoyed it more than last year.",
                "author": "Ozella Sipes",
                "date": datetime.now().isoformat(),
            },
        ],
        "vacancy": True,
        "description": "40 bed summer hostel about 3 miles from Gillingham.",
    }

    # Insert the document in the hotel collection.
    insert_result = hotel_collection.insert("hotel-123", document)

    # Print the result's CAS metadata to the console.
    print("CAS:", insert_result.cas)
    # end::kv-insert[]


def insert_with_opts():
    print("\n[kv-insert-with-opts]")
    # tag::kv-insert-with-opts[]
    document = {
        "id": 456,
        "title": "Ardèche",
        "name": "La Pradella",
        "address": "rue du village, 07290 Preaux, France",
        "phone": "+33 4 75 32 08 52",
        "url": "http://www.lapradella.fr",
        "country": "France",
        "city": "Preaux",
        "state": "Rhône-Alpes",
        "vacancy": False,
    }
    # Insert the document with an expiry time option of 60 seconds.
    insert_result = hotel_collection.insert(
        "hotel-456", document, InsertOptions(expiry=timedelta(seconds=60))
    )

    # Print the result's CAS metadata to the console.
    print("CAS:", insert_result.cas)
    # end::kv-insert-with-opts[]


def get():
    print("\n[kv-get]")
    # tag::kv-get[]
    get_result = hotel_collection.get("hotel-123")

    # Print some result metadata to the console.
    print("CAS:", get_result.cas)
    print("Data: {}".format(get_result.content_as[dict]))
    # end::kv-get[]


def get_with_opts():
    print("\n[kv-get-with-opts]")
    # tag::kv-get-with-opts[]
    get_result = hotel_collection.get(
        "hotel-456", GetOptions(with_expiry=True)
    )

    # Print some result metadata to the console.
    print("CAS:", get_result.cas)
    print("Data: {}".format(get_result.content_as[dict]))
    print("Expiry time: {}".format(get_result.expiryTime))
    # end::kv-get-with-opts[]


def get_subdoc():
    print("\n[kv-get-subdoc]")
    # tag::kv-get-subdoc[]
    lookup_in_result = hotel_collection.lookup_in(
        "hotel-123", [subdocument.get("geo")]
    )
    print("CAS:", lookup_in_result.cas)
    print("Data:", lookup_in_result.content_as[dict](0))
    # end::kv-get-subdoc[]


def update_replace():
    print("\n[kv-update-replace]")
    # tag::kv-update-replace[]
    # Fetch an existing hotel document.
    get_result = hotel_collection.get("hotel-123")
    existing_doc = get_result.content_as[dict]

    # Get the current CAS value.
    current_cas = get_result.cas
    print("Current CAS:", get_result.cas)

    # Add a new review to the reviews array.
    existing_doc["reviews"].append({
        "content": "This hotel was cozy, conveniently located and clean.",
        "author": "Carmella O'Keefe",
        "date": datetime.now().isoformat(),
    })

    # Update the document with new data and pass the current CAS value.
    replace_result = hotel_collection.replace(
        "hotel-123", existing_doc, ReplaceOptions(cas=current_cas)
    )
    print("New CAS:", replace_result.cas)
    # end::kv-update-replace[]


def update_upsert():
    print("\n[kv-update-upsert]")
    # Create a document object.
    document = {
        "id": 123,
        "name": "Medway Youth Hostel",
        "address": "Capstone Road, ME7 3JE",
        "url": "http://www.yha.org.uk",
        "country": "United Kingdom",
        "city": "Medway",
        "state": None,
        "vacancy": True,
        "description": "40 bed summer hostel about 3 miles from Gillingham.",
    }

    # tag::kv-update-upsert[]
    # Update or create a document in the hotel collection.
    upsert_result = hotel_collection.upsert("hotel-123", document)

    # Print the result's CAS metadata to the console.
    print("CAS:", upsert_result.cas)
    # end::kv-update-upsert[]


def update_subdoc():
    print("\n[kv-update-subdoc]")
    # tag::kv-update-subdoc[]
    mutate_in_result = hotel_collection.mutate_in(
        "hotel-123", [subdocument.upsert("pets_ok", True)]
    )
    print("CAS:", mutate_in_result.cas)
    # end::kv-update-subdoc[]


def remove_subdoc():
    print("\n[kv-remove-subdoc]")
    # tag::kv-remove-subdoc[]
    mutate_in_result = hotel_collection.mutate_in(
        "hotel-123", [subdocument.remove("url")]
    )
    print("CAS:", mutate_in_result.cas)
    # end::kv-remove-subdoc[]


def remove():
    print("\n[kv-remove]")
    # tag::kv-remove[]
    remove_result = hotel_collection.remove("hotel-123")
    print("CAS:", remove_result.cas)
    # end::kv-remove[]


insert()
insert_with_opts()
get()
get_with_opts()
get_subdoc()
update_replace()
update_upsert()
update_subdoc()
remove_subdoc()
remove()
