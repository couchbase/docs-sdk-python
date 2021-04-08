'''
python -m pip install couchbase
python -m pip install fastapi
python -m pip install uvicorn

NOTE:  make sure to change into the working
    directory before running uvicorn

uvicorn caching_fastapi:app --reload

'''
from datetime import timedelta
from fastapi import FastAPI, HTTPException, Body

from acouchbase.cluster import Cluster
from couchbase.cluster import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException, \
    DocumentExistsException, DocumentNotFoundException
from couchbase.collection import InsertOptions, UpsertOptions


class CouchbaseClient(object):

    @classmethod
    async def create_client(_, *args, **kwargs):
        self = CouchbaseClient(*args)
        client = await self.ping()
        # need to check for more than just a result
        # shown as example starting point
        if not client:
            await self.connect(**kwargs)
        return self

    _instance = None

    def __new__(cls, host, bucket, username, pw):
        if CouchbaseClient._instance is None:
            CouchbaseClient._instance = object.__new__(cls)
            CouchbaseClient._instance.host = host
            CouchbaseClient._instance.bucket_name = bucket
            CouchbaseClient._instance.username = username
            CouchbaseClient._instance.password = pw
        return CouchbaseClient._instance

    async def connect(self, **kwargs):
        # note: kwargs would be how one could pass in
        #       more info for client config
        # note:  use couchbases:// if using https
        conn_str = 'couchbase://{0}'.format(self.host)

        try:
            cluster_opts = ClusterOptions(
                authenticator=PasswordAuthenticator(
                    self.username, self.password))
            self._cluster = Cluster(conn_str, options=cluster_opts)
            self._bucket = self._cluster.bucket(self.bucket_name)
            await self._bucket.on_connect()
            self._collection = self._bucket.default_collection()
        except CouchbaseException as error:
            print('Could not connect to cluster. Error: {}'.format(error))
            raise

    async def ping(self):
        try:
            return not self._bucket.closed
        except AttributeError:
            # if the _bucket attr doesn't exist, neither does the client
            return False

    async def get(self, key, **kwargs):
        # note: kwargs would be how one could pass in
        #       more info for GetOptions
        return await self._collection.get(key)

    async def insert(self, key, doc, **kwargs):
        opts = InsertOptions(expiry=kwargs.get('expiry', None))
        return await self._collection.insert(key, doc, opts)

    async def upsert(self, key, doc, **kwargs):
        opts = UpsertOptions(expiry=kwargs.get('expiry', None))
        return await self._collection.upsert(key, doc, opts)

    async def remove(self, key, **kwargs):
        return await self._collection.remove(key)


# done for example purposes only, some
# sort of configuration should be used
db_info = {
    'host': 'localhost',
    'bucket': 'default',
    'username': 'Administrator',
    'password': 'password'
}


EXPIRY = timedelta(minutes=1)
app = FastAPI()

# TODO:  utilize fastapi.Depends()


@app.get('/')
async def ping():
    try:
        cb = await CouchbaseClient.create_client(*db_info.values())
        if await cb.ping():
            return 'Cluster is ready!'
        return 'Cluster not ready.'
    except CouchbaseException as e:
        return HTTPException(status_code=500,
                             detail='Unexpected error: {}'.format(e))


@app.get('/{key}')
async def get(key: str):
    try:
        cb = await CouchbaseClient.create_client(*db_info.values())
        res = await cb.get(key)
        return res.content_as[dict]
    except DocumentNotFoundException:
        return HTTPException(status_code=404,
                             detail='Key not found')
    except CouchbaseException as e:
        return HTTPException(status_code=500,
                             detail='Unexpected error: {}'.format(e))


@app.post('/{key}')
async def post(key: str, request: dict = Body(...)):
    try:
        cb = await CouchbaseClient.create_client(*db_info.values())
        await cb.insert(key, request, expiry=EXPIRY)
        return 'OK'
    except DocumentExistsException:
        return HTTPException(status_code=409,
                             detail='Key already exists')
    except CouchbaseException as e:
        return HTTPException(status_code=500,
                             detail='Unexpected error: {}'.format(e))


@app.put('/{key}')
async def put(key: str, request: dict = Body(...)):
    try:
        cb = await CouchbaseClient.create_client(*db_info.values())
        await cb.upsert(key, request, expiry=EXPIRY)
        return 'OK'
    except CouchbaseException as e:
        return HTTPException(status_code=500,
                             detail='Unexpected error: {}'.format(e))


@app.delete('/{key}')
async def delete(key):
    try:
        cb = await CouchbaseClient.create_client(*db_info.values())
        await cb.remove(key)
        return 'OK'
    except DocumentNotFoundException:
        return HTTPException(status_code=404,
                             detail='Key not found')
    except CouchbaseException as e:
        return HTTPException(status_code=500,
                             detail='Unexpected error: {}'.format(e))
