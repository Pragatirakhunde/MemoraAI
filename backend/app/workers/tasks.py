from app.database.postgres import SessionLocal
from app.models.data_source import DataSource
from app.models.sync_job import SyncJob
from app.repositories.sync_job_repository import SyncJobRepository
from app.services.sync_service import SyncService

from app.workers.celery_app import celery_app


@celery_app.task(
    bind=True,
    name="app.workers.tasks.sync_data_source_task",
)
def sync_data_source_task(
    self,
    data_source_id: int,
    sync_job_id: int,
):
    """
    Background task that executes synchronization
    for one data source.
    """

    db = SessionLocal()

    try:

        data_source = db.get(
            DataSource,
            data_source_id,
        )

        job = db.get(
            SyncJob,
            sync_job_id,
        )

        if job is None:
            return {
                "status": "failed",
                "data_source_id": data_source_id,
                "sync_job_id": sync_job_id,
                "message": "Sync job not found",
            }

        if data_source is None:

            SyncJobRepository.update(
                db,
                job,
                status="failed",
                error_message="Data source not found",
            )

            return {
                "status": "failed",
                "data_source_id": data_source_id,
                "sync_job_id": sync_job_id,
                "message": "Data source not found",
            }

        if data_source.status != "active":

            SyncJobRepository.update(
                db,
                job,
                status="failed",
                error_message="Data source is not active",
            )

            return {
                "status": "skipped",
                "data_source_id": data_source_id,
                "sync_job_id": sync_job_id,
                "message": "Data source is not active",
            }

        job = SyncService.run_sync(
            db=db,
            data_source=data_source,
            job=job,
        )

        return {
            "status": job.status,
            "data_source_id": data_source_id,
            "sync_job_id": job.id,
            "files_found": job.files_found,
            "files_processed": job.files_processed,
            "error_message": job.error_message,
        }

    except Exception as exc:

        return {
            "status": "failed",
            "data_source_id": data_source_id,
            "sync_job_id": sync_job_id,
            "message": str(exc),
        }

    finally:

        db.close()


@celery_app.task(
    name="app.workers.tasks.schedule_active_data_sources",
)
def schedule_active_data_sources():
    """
    Finds all active data sources and queues
    synchronization tasks.
    """

    db = SessionLocal()

    queued_jobs = []

    try:

        data_sources = (
            db.query(DataSource)
            .filter(
                DataSource.status == "active"
            )
            .all()
        )

        for data_source in data_sources:

            existing_job = (
                db.query(SyncJob)
                .filter(
                    SyncJob.data_source_id
                    == data_source.id,
                    SyncJob.status.in_(
                        ["pending", "running"]
                    ),
                )
                .order_by(
                    SyncJob.created_at.desc()
                )
                .first()
            )

            # Prevent duplicate syncs
            if existing_job is not None:
                continue

            # Create pending job before sending task
            job = SyncJobRepository.create(
                db,
                data_source.id,
            )

            try:

                task = sync_data_source_task.delay(
                    data_source.id,
                    job.id,
                )

                queued_jobs.append(
                    {
                        "data_source_id": data_source.id,
                        "sync_job_id": job.id,
                        "task_id": task.id,
                    }
                )

            except Exception as exc:

                SyncJobRepository.update(
                    db,
                    job,
                    status="failed",
                    error_message=str(exc),
                )

        return {
            "status": "completed",
            "queued": len(queued_jobs),
            "jobs": queued_jobs,
        }

    finally:

        db.close()