from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.auth.roles import require_admin
from app.database.postgres import get_db
from app.models.user import User
from app.models.sync_job import SyncJob

from app.repositories.data_source_repository import (
    DataSourceRepository,
)

from app.repositories.sync_job_repository import (
    SyncJobRepository,
)

from app.schemas.sync_job import SyncJobResponse
from app.services.sync_service import SyncService
from app.workers.tasks import sync_data_source_task

from app.workers.tasks import (
    schedule_active_data_sources,
)


router = APIRouter(
    prefix="/sync",
    tags=["Synchronization"],
)


@router.post(
    "/data-sources/{data_source_id}",
    response_model=SyncJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def sync_data_source(
    data_source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    data_source = DataSourceRepository.get_by_id(
        db,
        data_source_id,
        current_user.organization_id,
    )

    if data_source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    return SyncService.run_sync(
        db,
        data_source,
    )


@router.get(
    "/jobs",
    response_model=list[SyncJobResponse],
)
def get_sync_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    data_sources = DataSourceRepository.get_all(
        db,
        current_user.organization_id,
    )

    data_source_ids = [
        source.id
        for source in data_sources
    ]

    return SyncJobRepository.get_all_by_data_sources(
        db,
        data_source_ids,
    )


@router.get(
    "/jobs/{job_id}",
    response_model=SyncJobResponse,
)
def get_sync_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    job = SyncJobRepository.get_by_id(
        db,
        job_id,
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sync job not found",
        )

    data_source = DataSourceRepository.get_by_id(
        db,
        job.data_source_id,
        current_user.organization_id,
    )

    if data_source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sync job not found",
        )

    return job

@router.post(
    "/data-sources/{data_source_id}/background",
    response_model=SyncJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def queue_background_sync(
    data_source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    data_source = DataSourceRepository.get_by_id(
        db,
        data_source_id,
        current_user.organization_id,
    )

    if data_source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    existing_job = (
        db.query(SyncJob)
        .filter(
            SyncJob.data_source_id == data_source.id,
            SyncJob.status.in_(
                ["pending", "running"]
            ),
        )
        .order_by(
            SyncJob.created_at.desc()
        )
        .first()
    )

    if existing_job is not None:
        return existing_job

    job = SyncJobRepository.create(
        db,
        data_source.id,
    )

    db.commit()
    db.refresh(job)

    try:
        sync_data_source_task.delay(
            data_source.id,
            job.id,
        )

    except Exception as exc:
        SyncJobRepository.update(
            db,
            job,
            status="failed",
            error_message=str(exc),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue background sync",
        )

    return job

@router.post(
    "/background",
    status_code=status.HTTP_202_ACCEPTED,
)
def queue_all_background_syncs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    task = schedule_active_data_sources.delay()

    return {
        "status": "queued",
        "message": "Synchronization queued for active data sources",
        "task_id": task.id,
    }