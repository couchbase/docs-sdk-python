'''
python -m pip install couchbase
python -m pip install flask

export FLASK_APP=caching_flask && \
export FLASK_ENV=development

NOTE:  make sure to change into the working
    directory before running flask

flask run

'''
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, request

from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, InsertOptions, UpsertOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import (
    CouchbaseException,
    DocumentExistsException,
    DocumentNotFoundException)
from couchbase.diagnostics import PingState


class CouchbaseClient(object):

    @classmethod
    def create_client(_, *args, **kwargs):
        self = CouchbaseClient(*args)
        connected = self.ping()
        if not connected:
            self.connect(**kwargs)
        return self

    _instance = None

    def __new__(cls, host, bucket, username, pw):
        if CouchbaseClient._instance is None:
            CouchbaseClient._instance = object.__new__(cls)
            CouchbaseClient._instance.host = host
            CouchbaseClient._instance.bucket_name = bucket
            CouchbaseClient._instance.username = username
            CouchbaseClient._instance.password = pw
            CouchbaseClient._instance._cluster = None
        return CouchbaseClient._instance

    def connect(self, **kwargs):
        # note: kwargs would be how one could pass in
        #       more info for client config
        conn_str = 'couchbase://{0}'.format(self.host)

        try:
            cluster_opts = ClusterOptions(
                authenticator=PasswordAuthenticator(
                    self.username, self.password))
            self._cluster = Cluster.connect(conn_str, options=cluster_opts)
            self._bucket = self._cluster.bucket(self.bucket_name)
            self._collection = self._bucket.default_collection()
        except CouchbaseException as error:
            print('Could not connect to cluster. Error: {}'.format(error))
            raise

    def ping(self):
        if self._cluster is None:
            return False
        result = self._cluster.ping()
        for _, reports in result.endpoints.items():
            for report in reports:
                if not report.state == PingState.OK:
                    return False
        return True

    def get(self, key, **kwargs):
        return self._collection.get(key)

    def insert(self, key, doc, **kwargs):
        opts = InsertOptions(expiry=kwargs.get('expiry', None))
        return self._collection.insert(key, doc, opts)

    def upsert(self, key, doc, **kwargs):
        opts = UpsertOptions(expiry=kwargs.get('expiry', None))
        return self._collection.upsert(key, doc, opts)

    def remove(self, key, **kwargs):
        return self._collection.remove(key)


app = Flask(__name__)


@app.route('/')
def ping():
    try:
        if cb.ping():
            return 'Cluster is ready!'
        return 'Cluster not ready.'
    except CouchbaseException as e:
        return 'Unexpected error: {}'.format(e), 500

# tag::get[]
@app.route('/<key>', methods=['GET'])
def get(key):
    try:
        res = cb.get(key)
        return jsonify(res.content_as[dict])
    except DocumentNotFoundException:
        return 'Key not found', 404
    except CouchbaseException as e:
        return 'Unexpected error: {}'.format(e), 500
# end::get[]

# tag::cache-miss[]
def fetch_from_source(key):
    # Stands in for the system of record the cache sits in front of,
    # such as a relational database or a slower upstream service.
    return {'id': key, 'fetched_at': datetime.now(timezone.utc).isoformat()}


@app.route('/read-through/<key>', methods=['GET'])
def read_through(key):
    try:
        return jsonify(cb.get(key).content_as[dict])
    except DocumentNotFoundException:
        pass
    except CouchbaseException as e:
        return 'Unexpected error: {}'.format(e), 500

    doc = fetch_from_source(key)
    if doc is None:
        return 'Key not found', 404
    try:
        cb.upsert(key, doc, expiry=EXPIRY)
    except CouchbaseException as e:
        # The caller still gets the data; the next miss tries the write again.
        app.logger.warning('Could not cache %s: %s', key, e)
    return jsonify(doc)
# end::cache-miss[]

# tag::post[]
@app.route('/<key>', methods=['POST'])
def post(key):
    try:
        cb.insert(key, request.json, expiry=EXPIRY)
        return 'OK'
    except DocumentExistsException:
        return 'Key already exists', 409
    except CouchbaseException as e:
        return 'Unexpected error: {}'.format(e), 500
# end::post[]


# tag::put[]
@app.route('/<key>', methods=['PUT'])
def put(key):
    try:
        cb.upsert(key, request.json, expiry=EXPIRY)
        return 'OK'
    except CouchbaseException as e:
        return 'Unexpected error: {}'.format(e), 500
# end::put[]


# tag::delete[]
@app.route('/<key>', methods=['DELETE'])
def delete(key):
    try:
        cb.remove(key)
        return 'OK'
    except DocumentNotFoundException:
        # Document already deleted / never existed
        return 'Key does not exist', 404
# end::delete[]


# done for example purposes only, some
# sort of configuration should be used
db_info = {
    'host': 'your-ip',
    'bucket': 'default',
    'username': 'Administrator',
    'password': 'password'
}

EXPIRY = timedelta(minutes=1)
cb = CouchbaseClient.create_client(*db_info.values())

if __name__ == '__main__':
    app.run()
