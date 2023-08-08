import uuid

from couchbase.mutation_state import MutationState
from couchbase.cluster import QueryScanConsistency
# tag::n1ql_basic_example[]
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, QueryOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException

cluster = Cluster.connect(
    "couchbase://your-ip",
    ClusterOptions(PasswordAuthenticator("Administrator", "password")))
bucket = cluster.bucket("travel-sample")
collection = bucket.default_collection()

try:
    result = cluster.query(
        "SELECT * FROM `travel-sample`.inventory.airport LIMIT 10", QueryOptions(metrics=True))

    for row in result.rows():
        print(f"Found row: {row}")

    print(f"Report execution time: {result.metadata().metrics().execution_time()}")

except CouchbaseException as ex:
    import traceback
    traceback.print_exc()

# end::n1ql_basic_example[]

# tag::positional[]
result = cluster.query(
    "SELECT ts.* FROM `travel-sample`.inventory.airport WHERE city=$1",
    "San Jose")
# end::positional[]

# tag::positional_options[]
result = cluster.query(
    "SELECT ts.* FROM `travel-sample`.inventory.airport WHERE city=$1",
    QueryOptions(positional_parameters=["San Jose"]))
# end::positional_options[]

# tag::named_kwargs[]
result = cluster.query(
    "SELECT ts.* FROM `travel-sample`.inventory.airport WHERE city=$city",
    city='San Jose')
# end::named_kwargs[]

# tag::named_options[]
result = cluster.query(
    "SELECT ts.* FROM `travel-sample`.inventory.airport WHERE city=$city",
    QueryOptions(named_parameters={"city": "San Jose"}))
# end::named_options[]

# tag::iterating[]
result = cluster.query(
    "SELECT * FROM `travel-sample`.inventory.airline LIMIT 10")

# iterate over rows
for row in result:
    # each row is an instance of the query call
    try:
        name = row["airline"]["name"]
        callsign = row["airline"]["callsign"]
        print(f"Airline name: {name}, callsign: {callsign}")
    except KeyError:
        print("Row does not contain 'name' key")
# end::iterating[]

# tag::print_metrics[]

result = cluster.query("SELECT 1=1", QueryOptions(metrics=True))
for row in result:
    print(f"Result: {row}")
print(f"Execution time: {result.metadata().metrics().execution_time()}")

# end::print_metrics[]

# tag::scan_consistency[]
result = cluster.query(
    "SELECT * FROM `travel-sample`.inventory.airline LIMIT 10",
    QueryOptions(scan_consistency=QueryScanConsistency.REQUEST_PLUS))
# end::scan_consistency[]

# tag::ryow[]
new_hotel = {
    "callsign": None,
    "country": "United States",
    "iata": "TX",
    "icao": "TX99",
    "id": 123456789,
    "name": "Howdy Airlines",
    "type": "airline"
}

res = collection.upsert(
    "airline_{}".format(new_hotel["id"]), new_hotel)

ms = MutationState(res)

result = cluster.query(
    "SELECT ts.* FROM `travel-sample`.inventory.airline LIMIT 10",
    QueryOptions(consistent_with=ms))
# end::ryow[]

# tag::client_context_id[]
result = cluster.query(
    "SELECT ts.* FROM `travel-sample`.inventory.hotel LIMIT 10",
    QueryOptions(client_context_id="user-44{}".format(uuid.uuid4())))

# end::client_context_id[]

# tag::read_only[]
result = cluster.query(
    "SELECT ts.* FROM `travel-sample`.inventory.hotel LIMIT 10",
    QueryOptions(read_only=True))
# end::read_only[]

# tag::scope[]
agent_scope = bucket.scope("inventory")

result = agent_scope.query(
        "SELECT a.* FROM `airline` a WHERE a.country=$country LIMIT 10",
        country='France')
# end::scope[]
