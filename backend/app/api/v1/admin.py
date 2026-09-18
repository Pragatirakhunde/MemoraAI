from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.auth.roles import require_admin
from app.database.postgres import get_db
from app.schemas.admin_dashboard import (
    AdminDashboardResponse,
)
from app.services.admin_dashboard_service import (
    AdminDashboardService,
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse,
)
def get_admin_dashboard(
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    return AdminDashboardService.get_dashboard(
        db=db,
        organization_id=current_user.organization_id,
    )