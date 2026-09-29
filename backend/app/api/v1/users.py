from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.auth.roles import require_admin
from app.database.postgres import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.schemas.department import (
    DepartmentAssignmentRequest,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return UserService.create_employee(
            db=db,
            organization_id=current_user.organization_id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return UserService.get_users(
        db,
        current_user.organization_id,
    )

@router.get(
    "/pending",
    response_model=list[UserResponse],
)
def get_pending_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return UserService.get_pending_users(
        db,
        current_user.organization_id,
    )

@router.patch(
    "/{user_id}/approve",
    response_model=UserResponse,
)
def approve_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        user = UserService.approve_user(
            db,
            user_id,
            current_user.organization_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

@router.patch(
    "/{user_id}/reject",
    response_model=UserResponse,
)
def reject_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        user = UserService.reject_user(
            db,
            user_id,
            current_user.organization_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = UserService.get_user(
        db,
        user_id,
        current_user.organization_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = UserService.deactivate_user(
        db,
        user_id,
        current_user.organization_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

@router.patch(
    "/{user_id}/department",
    response_model=UserResponse,
)
def assign_department(
    user_id: int,
    data: DepartmentAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):

    try:
        user = UserService.assign_department(
            db=db,
            user_id=user_id,
            organization_id=current_user.organization_id,
            department_id=data.department_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user