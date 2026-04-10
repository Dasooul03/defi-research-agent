from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request
from starlette.responses import Response


class InMemoryRateLimiter:
    """Simple per-IP sliding-window limiter for API hardening in MVP stage."""

    def __init__(self, limit_per_minute: int) -> None:
        self.limit_per_minute = max(limit_per_minute, 0)
        self._records: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, now: float) -> None:
        if self.limit_per_minute <= 0:
            return

        window_start = now - 60.0
        bucket = self._records[key]

        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) >= self.limit_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        bucket.append(now)


async def request_observability_middleware(
    request: Request,
    call_next: Callable[[Request], Any],
) -> Response:
    logger = logging.getLogger("defi.api")
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    limiter: InMemoryRateLimiter | None = getattr(request.app.state, "rate_limiter", None)
    if limiter is not None:
        client_ip = request.client.host if request.client else "unknown"
        limiter.check(key=client_ip, now=time.time())

    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000

    response.headers["X-Request-Id"] = request_id
    response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"

    logger.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": round(elapsed_ms, 2),
        },
    )
    return response
