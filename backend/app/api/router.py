from fastapi import APIRouter

from app.api.v1.auth.router import router as auth_router
from app.api.v1.database import router as database_router
from app.api.v1.health import router as health_router
from app.api.v1.organizations import router as organizations_router
from app.api.v1.users import router as users_router
from app.api.v1.data_sources import router as data_sources_router
from app.api.v1.sync import router as sync_router
from app.api.v1.documents import router as documents_router


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(database_router)
api_router.include_router(organizations_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(data_sources_router)
api_router.include_router(sync_router)
api_router.include_router(documents_router)