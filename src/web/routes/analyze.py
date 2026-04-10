from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.agents.orchestrator import AgentOrchestrator
from src.web.schemas import APIResponse, AnalyzeRequest

router = APIRouter(tags=["analyze"])
orchestrator = AgentOrchestrator()


@router.post("/analyze", response_model=APIResponse)
def analyze(payload: AnalyzeRequest) -> APIResponse:
    try:
        result = orchestrator.run_analysis(payload.query, payload.protocol)
        return APIResponse(success=True, data=result)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc
