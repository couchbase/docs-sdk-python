"""
Make sure to install the following for the example to work:
    python3 -m pip install orjson msgpack

Must have Couchbase Python SDK v 3.2.2 or greater to use Transcoders
"""

import traceback
from typing import Any, Tuple

import orjson
import msgpack

from couchbase.cluster import Cluster, ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.collection import GetOptions, UpsertOptions
from couchbase.exceptions import CouchbaseException, ValueFormatException
from couchbase.transcoder import RawJSONTranscoder, RawStringTranscoder, RawBinaryTranscoder, Transcoder

cluster = Cluster("couchbase://localhost", ClusterOptions(
    PasswordAuthenticator("Administrator", "password")))
bucket = cluster.bucket("default")
collection = bucket.default_collection()

# tag::raw_json_encode[]
transcoder = RawJSONTranscoder()
user = {"name": "John Smith", "age": 27}

data = orjson.dumps(user)
try:
    _ = collection.upsert(
        "john-smith", data, UpsertOptions(transcoder=transcoder))
except (ValueFormatException, CouchbaseException) as ex:
    traceback.print_exc()
# end::raw_json_encode[]

# tag::raw_json_decode[]
try:
    get_result = collection.get("john-smith", GetOptions(transcoder=transcoder))
except (ValueFormatException, CouchbaseException) as ex:
    traceback.print_exc()

decoded = orjson.loads(get_result.content)
assert decoded == user
# end::raw_json_decode[]

# tag::raw_string_transcoder[]
transcoder = RawStringTranscoder()
input_str = "Hello, World!"

try:
    _ = collection.upsert(
        "key", input_str, UpsertOptions(transcoder=transcoder))

    get_result = collection.get("key", GetOptions(transcoder=transcoder))
except (ValueFormatException, CouchbaseException) as ex:
    traceback.print_exc()

assert get_result.content == input_str
# end::raw_string_transcoder[]

# tag::raw_binary_transcoder[]
transcoder = RawBinaryTranscoder()
input_bytes = bytes("Hello, World!", "utf-8")

try:
    _ = collection.upsert(
        "key", input_bytes, UpsertOptions(transcoder=transcoder))

    get_result = collection.get("key", GetOptions(transcoder=transcoder))
except (ValueFormatException, CouchbaseException) as ex:
    traceback.print_exc()

assert get_result.content == input_bytes
# end::raw_binary_transcoder[]


# tag::create_custom_transcoder[]
class MessagePackTranscoder(Transcoder):
    _CUSTOM_FLAGS = (1 << 24) | (ord("M") << 16) | (ord("P") << 8) | (ord("K") << 0)

    def encode_value(self,  # type: "MessagePackTranscoder"
                     value  # type: Any
                     ) -> Tuple[bytes, int]:

        try:
            packed = msgpack.packb(value)
            return packed, self._CUSTOM_FLAGS
        except Exception as ex:
            # Implement custom exception handling
            print("Exception: {}".format(ex))
            raise

    def decode_value(self,  # type: "MessagePackTranscoder"
                     value,  # type: bytes
                     flags  # type: int
                     ) -> bytes:

        if flags != self._CUSTOM_FLAGS:
            raise ValueError("Unexpected flags value.")

        try:
            return msgpack.unpackb(value)
        except Exception as ex:
            # Implement custom exception handling
            print("Exception: {}".format(ex))
            raise
# end::create_custom_transcoder[]


# tag::use_custom_transcoder[]
transcoder = MessagePackTranscoder()
user = {"name": "John Smith", "age": 27}

try:
    _ = collection.upsert(
        "mpk_key", user, UpsertOptions(transcoder=transcoder))

    get_result = collection.get("mpk_key", GetOptions(transcoder=transcoder))
except (ValueFormatException, CouchbaseException) as ex:
    traceback.print_exc()

assert get_result.content == user
# end::use_custom_transcoder[]
