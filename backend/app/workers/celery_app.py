from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "enterprise_memory_engine",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    timezone="UTC",
    enable_utc=True,

    task_track_started=True,

    broker_connection_retry_on_startup=True,

    result_expires=3600,
)


celery_app.conf.beat_schedule = {
    "sync-active-data-sources": {
        "task": "app.workers.tasks.schedule_active_data_sources",
        "schedule": settings.SYNC_INTERVAL_SECONDS,
    },
}