from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.auth.roles import require_admin
from app.database.postgres import get_db
from app.models.user import User
from app.schemas.data_source import (
    DataSourceCreate,
    DataSourceResponse,
)
from app.services.data_source_service import (
    DataSourceService,
)
from app.services.connector_service import ConnectorService


router = APIRouter(
    prefix="/data-sources",
    tags=["Data Sources"],
)


@router.post(
    "",
    response_model=DataSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_data_source(
    data: DataSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return DataSourceService.create(
            db=db,
            organization_id=current_user.organization_id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[DataSourceResponse],
)
def get_data_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return DataSourceService.get_all(
        db,
        current_user.organization_id,
    )


@router.get(
    "/{data_source_id}",
    response_model=DataSourceResponse,
)
def get_data_source(
    data_source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):

    data_source = DataSourceService.get_by_id(
        db,
        data_source_id,
        current_user.organization_id,
    )

    if data_source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    return data_source


@router.patch(
    "/{data_source_id}/deactivate",
    response_model=DataSourceResponse,
)
def deactivate_data_source(
    data_source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):

    data_source = DataSourceService.deactivate(
        db,
        data_source_id,
        current_user.organization_id,
    )

    if data_source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    return data_source

@router.post(
    "/{data_source_id}/validate",
)
def validate_data_source(
    data_source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    data_source = DataSourceService.get_by_id(
        db,
        data_source_id,
        current_user.organization_id,
    )

    if data_source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    result = ConnectorService.validate(
        source_type=data_source.source_type,
        config=data_source.config,
    )

    if result["valid"]:
        data_source.status = "active"
    else:
        data_source.status = "error"

    db.commit()

    return {
        "data_source_id": data_source.id,
        "status": data_source.status,
        **result,
    }