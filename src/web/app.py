from __future__ import annotations

from fastapi import FastAPI

from src.web.routes.analyze import router as analyze_router
from src.web.routes.chat import router as chat_router
from src.web.routes.health import router as health_router
from src.web.routes.report import router as report_router


def create_app() -> FastAPI:
    app = FastAPI(title="DeFi Research Agent", version="0.1.0")

    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(analyze_router)
    app.include_router(report_router)

    return app
