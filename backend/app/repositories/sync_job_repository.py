from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sync_job import SyncJob


class SyncJobRepository:

    @staticmethod
    def create(
        db: Session,
        data_source_id: int,
    ) -> SyncJob:

        job = SyncJob(
            data_source_id=data_source_id,
            status="pending",
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        return job

    @staticmethod
    def get_by_id(
        db: Session,
        job_id: int,
    ) -> SyncJob | None:

        return db.get(SyncJob, job_id)

    @staticmethod
    def get_all_by_data_sources(
        db: Session,
        data_source_ids: list[int],
    ) -> list[SyncJob]:

        if not data_source_ids:
            return []

        statement = (
            select(SyncJob)
            .where(
                SyncJob.data_source_id.in_(
                    data_source_ids
                )
            )
            .order_by(SyncJob.id.desc())
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def update(
        db: Session,
        job: SyncJob,
        status: str,
        files_found: int = 0,
        files_processed: int = 0,
        error_message: str | None = None,
    ):

        job.status = status
        job.files_found = files_found
        job.files_processed = files_processed
        job.error_message = error_message

        if status == "running":
            job.started_at = datetime.utcnow()

        if status in ("completed", "failed"):
            job.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(job)

        return job