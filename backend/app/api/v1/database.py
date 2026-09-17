from fastapi import APIRouter

from app.database.postgres import test_database_connection


router = APIRouter(tags=["Database"])


@router.get("/health/database")
def database_health():
    connected = test_database_connection()

    return {
        "database": "postgresql",
        "status": "connected" if connected else "disconnected",
    }