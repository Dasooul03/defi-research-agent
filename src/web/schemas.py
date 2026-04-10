from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)


class AnalyzeRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    protocol: str | None = Field(default=None)


class ReportRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    protocol: str | None = Field(default=None)


class APIResponse(BaseModel):
    success: bool
    data: dict[str, Any]
    error: str | None = None
