import couchbase, flask
from couchbase.cluster import Cluster, ClusterOptions
from couchbase_core.cluster import PasswordAuthenticator
from couchbase.exceptions import *
from couchbase.options import Durations

EXPIRY = Durations.minutes(1)

app = flask.Flask(__name__)

# Purposefully bad load-from-disk function
def getFromPersistent(key):
    v = None
    with open("./PersistentStorage.txt", mode='r') as f:
        for line in f:
            k,v = line.split('\t')
            if k == key:
                return json.loads(v[:-1])
    raise KeyNotFoundException("Key not present in permanent storage")

@app.route("/<key>", methods=["GET"]) 
def get(key):
    # try:
        res = COLLECTION.get(key)
        return flask.jsonify(res.content_as[dict])
    # except KeyNotFoundException:
    #     try:
    #         val = getFromPersistent(key)
    #         COLLECTION.insert(key, val, expiration = EXPIRY)
    #         return flask.jsonify(val)
    #     except KeyNotFoundException:
    #         return "Key not found", 404
    #     except CouchbaseError as e:
    #         return "Unexpected error: {}".format(e), 500
    # except CouchbaseError as e:
    #     return "Unexpected error: {}".format(e), 500


@app.route("/<key>", methods=["POST"]) 
def post(key):
    try:
        COLLECTION.insert(key, flask.request.json, expiration = EXPIRY)
        return "OK"
    except KeyExistsException:
        return "Key already exists", 409
    except CouchbaseError as e:
        return "Unexpected error: {}".format(e), 500

@app.route("/<key>", methods=["PUT"]) 
def put(key):
    try:
        COLLECTION.upsert(key, flask.request.json, expiration = EXPIRY)
        return "OK"
    except CouchbaseError as e:
        return "Unexpected error: {}".format(e), 500

@app.route("/<key>", methods=["DELETE"]) 
def delete(key):
    try:
        COLLECTION.remove(key)
        return "OK"
    except KeyNotFoundException:
        # Document already deleted / never existed
        return "Key does not exist", 404

cluster = Cluster('couchbase://10.112.195.101', ClusterOptions(PasswordAuthenticator('Administrator', 'password')))
cb = cluster.bucket('default')
COLLECTION = cb.default_collection()


app.run(host="0.0.0.0", port=8000)

