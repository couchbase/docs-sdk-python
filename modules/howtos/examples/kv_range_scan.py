from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator


cluster = Cluster.connect('couchbase://your-ip',
                          ClusterOptions(PasswordAuthenticator('Administrator',
                                                               'password')))
bucket = cluster.bucket('default')
collection = bucket.default_collection()

# tag::range_scan_all_documents[]
from couchbase.kv_range_scan import RangeScan
result = collection.scan(RangeScan()) # <1>
for r in result:
    print(f'Found result, ID={r.id}, content={r.content_as[dict]}')
# end::range_scan_all_documents[]


# tag::range_scan_all_document_ids[]
from couchbase.options import ScanOptions
# ids_only via ScanOptions
result = collection.scan(RangeScan(), ScanOptions(ids_only=True))
# NOTE: An InvalidArgumentException is raised if content_as is 
# accessed when ids_only=True is used
for r in result:
    print(f'Found result, ID={r.id}')

# ids_only via kwargs
result = collection.scan(RangeScan(), ids_only=True)
for r in result:
    print(f'Found result, ID={r.id}')
# end::range_scan_all_document_ids[]

# tag::range_scan_prefix[]
from couchbase.kv_range_scan import PrefixScan
result = collection.scan(PrefixScan('alice::'))
for r in result:
    print(f'Found result, ID={r.id}, content={r.content_as[dict]}')
# tag::range_scan_prefix[]

# tag::range_scan_sample[]
from couchbase.kv_range_scan import SamplingScan
result = collection.scan(SamplingScan(100))
for r in result:
    print(f'Found result, ID={r.id}, content={r.content_as[dict]}')
# tag::range_scan_sample[]