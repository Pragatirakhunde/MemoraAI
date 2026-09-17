from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.postgres import get_db
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
)
from app.services.organization_service import OrganizationService
from app.api.v1.auth.roles import require_admin , require_employee


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        return OrganizationService.create_organization(
            db,
            data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[OrganizationResponse],
)
def get_organizations(
    db: Session = Depends(get_db),
    current_user=Depends(require_employee),
):
    return OrganizationService.get_all_organizations(db)


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_employee),
):
    organization = OrganizationService.get_organization(
        db,
        organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    return organization