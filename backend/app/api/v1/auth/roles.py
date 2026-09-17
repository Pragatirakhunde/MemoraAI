from fastapi import Depends, HTTPException, status

from app.api.v1.auth.dependencies import get_current_user


def require_admin(
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user


def require_employee(
    current_user=Depends(get_current_user),
):
    if current_user.role not in ("admin", "employee"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee access required",
        )

    return current_user