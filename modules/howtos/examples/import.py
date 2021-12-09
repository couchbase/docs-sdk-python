
from couchbase.cluster import Cluster, PasswordAuthenticator
import os
# tag::csv-tsv-import[]
import csv
# end::csv-tsv-import[]
# tag::json-jsonl-import[]
import json
# end::json-jsonl-import[]


# change to the directory of the script, where the various import.* files are
os.chdir(os.path.dirname(os.path.realpath(__file__)))


# tag::connect[]
cluster = Cluster(
    "couchbase://localhost",
    authenticator=PasswordAuthenticator(
        "Administrator", "password"))

bucket = cluster.bucket("travel-sample")

collection = bucket.scope("inventory").collection("airline")
# end::connect[]

# tag::key[]
def key(row):
    return "{type}_{id}".format(**row)
# end::key[]

# tag::process[]
def process(row):
    row["importer"] = "Python SDK"
    return row
# end::process[]

# tag::upsertDocument[]
def upsert(row):
    k = key(row)
    v = process(row)
    print(k, v)
    collection.upsert(k, v)
# end::upsertDocument[]

# tag::csvImport[]
def csv_import(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            upsert(row)
# end::csvImport[]
csv_import('import.csv')

# tag::csvImportMulti[]
# multi operations volatile as of SDK 3.2.3
def csv_import_multi(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        data = { key(row): process(row) for row in reader }
        print(data)
        collection.upsert_multi(data)
# end::csvImportMulti[]
csv_import_multi('import.csv')

# tag::tsvImport[]
def tsv_import(filename):
    with open(filename, newline='') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            upsert(row)
# end::tsvImport[]   
tsv_import('import.tsv') 

# tag::jsonImport[]
def json_import(filename):
    with open(filename) as jsonfile:
        data = json.load(jsonfile)
        for row in data:
            upsert(row)
# end::jsonImport[]
json_import('import.json') 

# tag::jsonlImport[]
def jsonl_import(filename):
    with open(filename) as jsonlfile:
        for line in jsonlfile:
            row = json.loads(line)
            upsert(row)
# end::jsonlImport[]
jsonl_import('import.jsonl') 

