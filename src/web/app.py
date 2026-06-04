from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from src.core.settings import get_settings, get_yaml_config
from src.web.middleware import InMemoryRateLimiter, request_observability_middleware
from src.web.routes.analyze import router as analyze_router
from src.web.routes.chat import router as chat_router
from src.web.routes.health import router as health_router
from src.web.routes.report import router as report_router


def create_app() -> FastAPI:
    settings = get_settings()
    config = get_yaml_config()

    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

    app = FastAPI(
        title=str(config.get("app", {}).get("name", "DeFi Research Agent")),
        version=str(config.get("app", {}).get("version", settings.app_version)),
    )

    cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.settings = settings
    rate_limit = int(config.get("api", {}).get("rate_limit_per_minute", settings.rate_limit_per_minute))
    app.state.rate_limiter = InMemoryRateLimiter(limit_per_minute=rate_limit)
    app.middleware("http")(request_observability_middleware)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "Request payload validation failed",
                "request_id": getattr(request.state, "request_id", None),
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "INTERNAL_ERROR",
                "message": str(exc),
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(analyze_router)
    app.include_router(report_router)

    # Mount frontend static files (built by Next.js export)
    static_dir = Path(__file__).resolve().parent.parent.parent / "static"
    if static_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app
