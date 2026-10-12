"""Prometheus metrics endpoint and basic counters for the Memora Celery worker.

The metrics HTTP server is started only when a Celery worker starts, not when
FastAPI or an ordinary management command imports celery_app.py.
"""
from __future__ import annotations

import logging
import threading
import time

from celery.signals import task_failure, task_postrun, task_prerun, worker_init
from prometheus_client import Counter, Histogram, start_http_server

logger = logging.getLogger(__name__)

TASKS_STARTED = Counter(
    "memora_celery_tasks_started_total",
    "Total number of Memora Celery tasks started.",
    ("task_name",),
)
TASKS_SUCCEEDED = Counter(
    "memora_celery_tasks_succeeded_total",
    "Total number of Memora Celery tasks that completed successfully.",
    ("task_name",),
)
TASKS_FAILED = Counter(
    "memora_celery_tasks_failed_total",
    "Total number of Memora Celery tasks that failed.",
    ("task_name",),
)
TASK_DURATION_SECONDS = Histogram(
    "memora_celery_task_duration_seconds",
    "Duration of Memora Celery task execution in seconds.",
    ("task_name",),
)

_started_at: dict[str, float] = {}
_started_at_lock = threading.Lock()


@worker_init.connect(weak=False)
def start_worker_metrics_server(**_kwargs) -> None:
    """Expose /metrics on port 9808 for the configured Prometheus scrape job."""
    # This project is run with Celery's solo pool on Windows. The worker_init
    # signal is emitted by the worker process, not merely by importing its app.
    try:
        start_http_server(port=9808, addr="0.0.0.0")
    except OSError as exc:
        # Keep the worker running if Prometheus metrics are unavailable, but
        # make the reason visible in the worker log.
        logger.error("Could not start Celery Prometheus metrics server on 0.0.0.0:9808: %s", exc)
    else:
        logger.info("Celery Prometheus metrics available on http://0.0.0.0:9808/metrics")


@task_prerun.connect(weak=False)
def record_task_start(sender=None, task_id=None, **_kwargs) -> None:
    task_name = getattr(sender, "name", "unknown") or "unknown"
    TASKS_STARTED.labels(task_name=task_name).inc()
    if task_id:
        with _started_at_lock:
            _started_at[task_id] = time.monotonic()


@task_postrun.connect(weak=False)
def record_task_finish(sender=None, task_id=None, state=None, **_kwargs) -> None:
    task_name = getattr(sender, "name", "unknown") or "unknown"
    if state == "SUCCESS":
        TASKS_SUCCEEDED.labels(task_name=task_name).inc()

    started = None
    if task_id:
        with _started_at_lock:
            started = _started_at.pop(task_id, None)
    if started is not None:
        TASK_DURATION_SECONDS.labels(task_name=task_name).observe(max(0.0, time.monotonic() - started))


@task_failure.connect(weak=False)
def record_task_failure(sender=None, task_id=None, **_kwargs) -> None:
    task_name = getattr(sender, "name", "unknown") or "unknown"
    TASKS_FAILED.labels(task_name=task_name).inc()
