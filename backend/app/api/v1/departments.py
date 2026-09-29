from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.v1.auth.roles import require_admin
from app.database.postgres import get_db
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
)
from app.services.department_service import DepartmentService


router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):

    try:
        return DepartmentService.create_department(
            db=db,
            organization_id=current_user.organization_id,
            name=data.name,
            description=data.description,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[DepartmentResponse],
)
def get_departments(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):

    return DepartmentService.get_departments(
        db=db,
        organization_id=current_user.organization_id,
    )