from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import global_exception_handler
from app.core.logging import logger
from app.monitoring.metrics import APP_INFO, HTTP_REQUESTS, HTTP_REQUEST_DURATION, metrics_asgi_app

logger.info("Starting Enterprise Memory Engine...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Memory Engine API",
    version=settings.APP_VERSION,
)

origins = [item.strip() for item in settings.CORS_ORIGINS.split(",") if item.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, global_exception_handler)
app.include_router(api_router)

if settings.PROMETHEUS_ENABLED:
    APP_INFO.labels(version=settings.APP_VERSION).set(1)
    app.mount("/metrics", metrics_asgi_app())


@app.middleware("http")
async def record_http_metrics(request: Request, call_next):
    path = request.url.path
    if not settings.PROMETHEUS_ENABLED or path.startswith("/metrics"):
        return await call_next(request)

    started = perf_counter()
    status_code = "500"
    try:
        response = await call_next(request)
        status_code = str(response.status_code)
        return response
    finally:
        route = request.scope.get("route")
        # Route templates avoid high-cardinality labels containing IDs/query data.
        route_label = getattr(route, "path", "unmatched") or "unmatched"
        HTTP_REQUESTS.labels(request.method, route_label, status_code).inc()
        HTTP_REQUEST_DURATION.labels(request.method, route_label).observe(perf_counter() - started)


@app.get("/", tags=["Root"])
def root():
    return {
        "success": True,
        "message": "Enterprise Memory Engine Backend Running",
        "version": settings.APP_VERSION,
    }
