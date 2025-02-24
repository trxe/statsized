from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from prometheus_client import start_http_server
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

class PrometheusMetrics:
    @classmethod
    def get(cls, metric_name: str):
        return metrics.get_meter(metric_name)

    @classmethod
    def create_counter(cls, metric_name: str, name: str, unit: str, description: str = "", callbacks = None):
        if callbacks != None:
            return cls.get(metric_name=metric_name).create_observable_counter(name, callbacks=callbacks, unit=unit, description=description)
        return cls.get(metric_name=metric_name).create_up_down_counter(name, unit=unit, description=description)

    @classmethod
    def create_gauge(cls, metric_name: str, name: str, unit: str, description: str = "", callbacks = None):
        if callbacks != None:
            return cls.get(metric_name=metric_name).create_observable_gauge(name, callbacks=callbacks, unit=unit, description=description)
        return cls.get(metric_name=metric_name).create_gauge(name, callbacks=callbacks, unit=unit, description=description)

    @classmethod
    def create_histogram(cls, metric_name: str, name: str, unit: str, description: str = "", buckets = None):
        return cls.get(metric_name=metric_name).create_histogram(name, unit, description, buckets)

    @classmethod
    def start(cls, host, port, service_name):
        # Service name is required for most backends
        cls.resource = Resource(attributes={
            SERVICE_NAME: service_name
        })

        # Start Prometheus client
        start_http_server(port=port, addr=host)
        # Initialize PrometheusMetricReader which pulls metrics from the SDK
        # on-demand to respond to scrape requests
        cls.reader = PrometheusMetricReader()
        cls.provider = MeterProvider(resource=cls.resource, metric_readers=[cls.reader])
        metrics.set_meter_provider(cls.provider)
