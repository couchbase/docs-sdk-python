import asyncio, time, aiofiles
from sanic import Sanic, response
from acouchbase.bucket import Bucket
from couchbase.exceptions import *
from couchbase.options import Durations

EXPIRY = Durations.minutes(1)
COLLECTION = None

app = Sanic()

def openCollection(connStr, user, passwd, bucket):
    bucket = Bucket(connStr, name=bucket, username=user, password=passwd)
    collection = bucket.default_collection()
    return collection

# Purposefully bad load-from-disk function
# (at least it's async)
async def getFromPersistent(key):
    v = None
    async with aiofiles.open("./PersistentStorage.txt", mode='r') as f:
        async for line in f:
            k,v = line.split('\t')
            if k == key:
                return json.loads(v[:-1])
    raise KeyNotFoundException("Key not present in permanent storage")

@app.route("/<key>", methods=["GET"]) 
async def get(request, key):
    try:
        res = await COLLECTION.get(key)
        return response.json(res.content_as[dict])
    except KeyNotFoundException:
        try:
            val = await getFromPersistent(key)
            await COLLECTION.insert(key, val, expiration = EXPIRY)
            return response.json(val)
        except KeyNotFoundException:
            return response.text("Key not found", status=404)
        except CouchbaseError as e:
            return response.text("Unexpected error: {}".format(e), status=500)
    except CouchbaseError as e:
        return response.text("Unexpected error: {}".format(e), status=500)
    
    
@app.route("/<key>", methods=["POST"]) 
async def post(request, key):
    try:
        await COLLECTION.insert(key, request.json, expiration = EXPIRY)
        return response.text("OK")
    except KeyExistsException:
        return response.text("Key already exists", status=409)
        pass
    except CouchbaseError as e:
        return response.text("Unexpected error: {}".format(e), status=500)

@app.route("/<key>", methods=["PUT"]) 
async def put(request, key):
    try:
        await COLLECTION.upsert(key, request.json, expiration = EXPIRY)
        return response.text("OK")
    except CouchbaseError as e:
        return response.text("Unexpected error: {}".format(e), status=500)

@app.route("/<key>", methods=["DELETE"]) 
async def delete(request, key):
    try:
        await COLLECTION.remove(key)
        return response.text("OK")
    except KeyNotFoundException:
        # Document already deleted / never existed
        return response.text("Key did not exist", status=410)

# Setup function
@app.listener('before_server_start')
async def setup_db(app, loop):
    global COLLECTION
    COLLECTION = openCollection("couchbase://localhost", "Administrator", "password", "default")
    await COLLECTION.connect()


app.run(host="0.0.0.0", port=8000)

