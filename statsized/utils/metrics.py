from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from prometheus_client import start_http_server
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

class NoopMetrics:
    exporter = ConsoleMetricExporter()
    metric_reader = PeriodicExportingMetricReader(exporter)
    provider = MeterProvider(metric_readers=[metric_reader])
    # Sets the global default meter provider
    metrics.set_meter_provider(provider)
    # Creates a meter from the global meter provider

    @classmethod
    def get(cls, metric_name: str):
        return metrics.get_meter(metric_name)

class OTLPMetrics:
    # Service name is required for most backends
    resource = Resource(attributes={
        SERVICE_NAME: "dice-service"
    })

    exporter = OTLPMetricExporter(endpoint="localhost:5555")
    metric_reader = PeriodicExportingMetricReader(exporter)
    provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(provider)

    @classmethod
    def get(cls, metric_name: str):
        return metrics.get_meter(metric_name)

class PrometheusMetrics:

    # Service name is required for most backends
    resource = Resource(attributes={
        SERVICE_NAME: "dice-service"
    })

    # Start Prometheus client
    start_http_server(port=9464, addr="localhost")
    # Initialize PrometheusMetricReader which pulls metrics from the SDK
    # on-demand to respond to scrape requests
    reader = PrometheusMetricReader()
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)

    @classmethod
    def get(cls, metric_name: str):
        return metrics.get_meter(metric_name)
