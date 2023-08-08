import time

from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import (
    BucketAlreadyExistsException,
    BucketDoesNotExistException)
from couchbase.management.buckets import (
    BucketSettings,
    ConflictResolutionType,
    CreateBucketSettings,
    BucketType)


def retry(func, *args, back_off=0.5, limit=5, **kwargs):
    for i in range(limit):
        try:
            return func(*args, **kwargs)
        except Exception:
            print(f"Retry in {(i + 1) * back_off} seconds...")
            time.sleep((i + 1) * back_off)

    raise Exception(f"Unable to successfully receive result from {func}")


# tag::create_bucket_mgr[]
cluster = Cluster(
    "couchbase://your-ip",
    authenticator=PasswordAuthenticator(
        "Administrator",
        "password"))
# For Server versions 6.5 or later you do not need to open a bucket here
bucket = cluster.bucket("travel-sample")
collection = bucket.default_collection()

bucket_manager = cluster.buckets()

# end::create_bucket_mgr[]

# tag::create_bucket[]
try:
    bucket_manager.create_bucket(
        CreateBucketSettings(
            name="hello",
            flush_enabled=True,
            ram_quota_mb=100,
            num_replicas=0,
            bucket_type=BucketType.COUCHBASE,
            conflict_resolution_type=ConflictResolutionType.SEQUENCE_NUMBER))
# end::create_bucket[]
except BucketAlreadyExistsException:
    print("hello bucket previously created.")

# Creating a bucket can take some time depending on what
# the cluster is doing, good to use retries
bucket = retry(bucket_manager.get_bucket, "hello")

# tag::get_and_update_bucket[]
bucket = bucket_manager.get_bucket("hello")
print(f"Found bucket: {bucket.name}")

bucket_manager.update_bucket(BucketSettings(name="hello", flush_enabled=True))
# end::get_and_update_bucket[]

# tag::flush_bucket[]
bucket_manager.flush_bucket("hello")
# end::flush_bucket[]

# tag::drop_bucket[]
bucket_manager.drop_bucket("hello")
# end::drop_bucket[]

# verify bucket dropped
try:
    bucket_manager.get_bucket("hello")
except BucketDoesNotExistException:
    print("hello bucket dropped.")
