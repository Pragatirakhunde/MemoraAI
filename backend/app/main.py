from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import global_exception_handler
from app.core.logging import logger

logger.info("Starting Enterprise Memory Engine...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Memory Engine API",
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(
    Exception,
    global_exception_handler,
)

app.include_router(api_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "success": True,
        "message": "Enterprise Memory Engine Backend Running",
        "version": "1.0.0",
    }

@app.get("/error")
def error():
    raise Exception("Testing Global Exception")