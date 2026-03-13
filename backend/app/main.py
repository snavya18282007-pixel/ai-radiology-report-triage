from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.routers.api import router as api_router
from app.routers.dashboard import router as dashboard_router
from app.routers.health import router as health_router
from app.routers.reports import router as reports_router


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(title=settings.app_name, version="1.0.0")

    app.include_router(health_router)
    app.include_router(reports_router)
    app.include_router(dashboard_router)
    app.include_router(api_router)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return app


app = create_app()
