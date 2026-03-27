import time
from datetime import timedelta

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.observability.otel_metrics import get_otel_meter
from couchbase.options import ClusterOptions

# Configuration
SERVICE_NAME = "couchbase-otel-metrics-example"
PROMETHEUS_PORT = 8000
METRICS_ENDPOINT = "http://localhost:4317"
CONNECTION_STRING = 'couchbase://localhost'
BUCKET_NAME = 'default'
USERNAME = 'Administrator'
PASSWORD = 'password'  # nosec

def setup_otel_metrics():
    """Setup OpenTelemetry for metrics."""

    # Create service resource
    resource = Resource.create(attributes={
        "service.name": SERVICE_NAME,
        "service.version": "1.0.0",
    })

    exporter = OTLPMetricExporter(
        endpoint=METRICS_ENDPOINT,
        insecure=True
    )
    reader = PeriodicExportingMetricReader(exporter, export_interval_millis=1000)

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[reader]
    )
    metrics.set_meter_provider(meter_provider)

    return meter_provider, get_otel_meter(meter_provider)

def print_banner():
    """Print example information banner."""
    print("\n" + "="*80)
    print("OpenTelemetry OTLP Metrics")
    print("Metrics (Prometheus)")
    print("="*80)
    print()

def perform_operations(collection, cluster):
    print("\n" + "-"*80)
    print("Performing Operations (Generating Metrics)")
    print("-"*80)
    print()

    # Test documents
    docs = {
        'metrics:1': {'name': 'Alice', 'age': 30, 'type': 'user', 'user_role': 'admin'},
        'metrics:2': {'name': 'Bob', 'age': 25, 'type': 'user', 'user_role': 'developer'},
        'metrics:3': {'name': 'Charlie', 'age': 35, 'type': 'user', 'user_role': 'manager'},
        'metrics:4': {'name': 'Diana', 'age': 28, 'type': 'user', 'user_role': 'designer'},
        'metrics:5': {'name': 'Eve', 'age': 32, 'type': 'user', 'user_role': 'analyst'},
    }

    # Upsert operations
    print("1. Upserting documents...")
    for key, doc in docs.items():
        result = collection.upsert(key, doc)
        print(f"   ✓ Upserted '{key}'")

    # Get operations (multiple rounds to generate histogram data)
    print("\n2. Retrieving documents (multiple rounds for histogram data)...")
    for round_num in range(1, 4):
        print(f"   Round {round_num}:")
        for key in docs.keys():
            result = collection.get(key)
            content = result.content_as[dict]
        print(f"     ✓ Retrieved all {len(docs)} documents")

    # Replace operations
    print("\n3. Replacing documents...")
    for key in list(docs.keys())[:3]:  # Just first 3
        get_result = collection.get(key)
        doc = get_result.content_as[dict]
        doc['updated'] = True
        collection.replace(key, doc, cas=get_result.cas)
        print(f"   ✓ Replaced '{key}'")

    # Touch operations
    print("\n4. Touching documents (updating expiry)...")
    for key in list(docs.keys())[3:]:  # Last 2
        collection.touch(key, timedelta(hours=1))
        print(f"   ✓ Touched '{key}'")

    # Query operation
    print("\n5. Executing N1QL query...")
    query = f"SELECT name, user_role FROM `{BUCKET_NAME}` WHERE type = 'user' LIMIT 3"  # nosec
    try:
        result = cluster.query(query)
        rows = list(result.rows())
        print(f"   ✓ Query returned {len(rows)} rows")
        for row in rows:
            print(f"      - {row['name']}: {row['user_role']}")
    except Exception as e:
        print(f"   ⚠ Query failed: {e}")

    # Cleanup
    print("\n6. Cleaning up...")
    for key in docs.keys():
        try:
            collection.remove(key)
            print(f"   ✓ Removed '{key}'")
        except Exception:  # nosec
            pass

    print("\n" + "-"*80)
    print("All operations completed!")
    print("-"*80)

def main():
    """Main execution function."""
    print_banner()
    meter_provider = None

    try:
        print("Setting up OpenTelemetry...")
        # tag::metrics-otel-prometheus[]
        # create service resource
        resource = Resource.create(attributes={
            "service.name": SERVICE_NAME,
            "service.version": "1.0.0",
        })

        # setup an exporter
        # This exporter exports traces on the OTLP protocol over GRPC to localhost:4317.
        exporter = OTLPMetricExporter(
            endpoint='http://localhost:4317',
            insecure=True
        )
        # setup a periodic reader to export metrics every 1000ms
        reader = PeriodicExportingMetricReader(exporter, export_interval_millis=1000)
        # create the meter provider with the resource and reader, then set it as global
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[reader]
        )
        metrics.set_meter_provider(meter_provider)

        # create the SDK's meter
        # required import: from couchbase.observability.otel_metrics import get_otel_meter
        couchbase_meter = get_otel_meter(meter_provider)

        # pass the meter to the Couchbase SDK via ClusterOptions
        opts = ClusterOptions(
            PasswordAuthenticator(USERNAME, PASSWORD),
            meter=couchbase_meter,   
        )

        cluster = Cluster.connect('couchbase://localhost', opts)
        # end::metrics-otel-prometheus[]
        bucket = cluster.bucket(BUCKET_NAME)
        collection = bucket.default_collection()
        print("✓ Connected to Couchbase\n")

        perform_operations(collection, cluster)

        print("\nClosing cluster connection...")
        cluster.close()
        
        # Give the periodic reader a moment to catch the final operations
        print("Flushing final metrics to OTLP Collector...")
        time.sleep(2)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # CRITICAL: This forces the final batch of metrics to be exported
        # before the Python script completely exits.
        if meter_provider:
            meter_provider.shutdown()
            print("✓ OpenTelemetry provider shut down gracefully.")

if __name__ == "__main__":
    main()