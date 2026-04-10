from __future__ import annotations

import time

from fastapi import APIRouter

from src.core.settings import get_settings

router = APIRouter(tags=["health"])
STARTED_AT = time.time()


@router.get("/health")
def health_check() -> dict[str, object]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "defi-research-agent",
        "version": settings.app_version,
        "env": settings.app_env,
        "uptime_seconds": round(time.time() - STARTED_AT, 2),
        "dependencies": {
            "openai_key_configured": bool(settings.openai_api_key),
        },
    }
