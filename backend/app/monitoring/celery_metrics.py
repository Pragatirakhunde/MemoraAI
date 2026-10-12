"""Prometheus metrics emitted by a running Celery worker process."""
from __future__ import annotations

import time

from celery.signals import task_postrun, task_prerun, worker_ready, worker_shutdown
from prometheus_client import Counter, Gauge, Histogram, start_http_server

from app.core.config import settings
from app.core.logging import logger

CELERY_TASKS = Counter(
    "memora_celery_tasks",
    "Celery task executions by task and final state.",
    ("task_name", "state"),
)
CELERY_TASK_DURATION = Histogram(
    "memora_celery_task_duration_seconds",
    "Celery task duration in seconds.",
    ("task_name",),
    buckets=(0.1, 0.5, 1, 2.5, 5, 10, 30, 60, 120, 300, 900),
)
CODEMIND_INDEXED_ITEMS = Counter(
    "memora_codemind_indexed_items",
    "Items processed by CodeMind repository indexing tasks.",
    ("kind",),
)

CELERY_WORKER_READY = Gauge(
    "memora_celery_worker_ready",
    "Whether the Celery worker has started its metrics endpoint.",
)

_started_at: dict[str, float] = {}
_metrics_server = None


@worker_ready.connect

def start_worker_metrics(**_kwargs):
    global _metrics_server
    if _metrics_server is not None:
        return
    try:
        _metrics_server, _thread = start_http_server(
            settings.CELERY_METRICS_PORT,
            addr="0.0.0.0",
        )
        CELERY_WORKER_READY.set(1)
        logger.info("Celery Prometheus metrics listening on port %s", settings.CELERY_METRICS_PORT)
    except OSError:
        # Do not crash task processing if another worker already owns the port.
        logger.exception("Could not start Celery metrics server on port %s", settings.CELERY_METRICS_PORT)


@worker_shutdown.connect

def mark_worker_stopped(**_kwargs):
    CELERY_WORKER_READY.set(0)


@task_prerun.connect

def record_task_start(task_id=None, **_kwargs):
    if task_id:
        _started_at[task_id] = time.monotonic()


@task_postrun.connect

def record_task_finish(task_id=None, task=None, state=None, **_kwargs):
    task_name = getattr(task, "name", "unknown") or "unknown"
    task_state = (state or "unknown").lower()
    CELERY_TASKS.labels(task_name=task_name, state=task_state).inc()
    started = _started_at.pop(task_id, None) if task_id else None
    if started is not None:
        CELERY_TASK_DURATION.labels(task_name=task_name).observe(time.monotonic() - started)
