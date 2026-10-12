from prometheus_client import Counter, Gauge, Histogram, make_asgi_app

HTTP_REQUESTS = Counter(
    "memora_http_requests",
    "HTTP requests served by the Memora API.",
    ("method", "route", "status"),
)
HTTP_REQUEST_DURATION = Histogram(
    "memora_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ("method", "route"),
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30),
)
APP_INFO = Gauge(
    "memora_app_info",
    "Build/runtime information for the Memora API.",
    ("version",),
)


def metrics_asgi_app():
    """Return an ASGI app that exposes Prometheus metrics at /metrics."""
    return make_asgi_app()
