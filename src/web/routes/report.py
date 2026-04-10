from __future__ import annotations

from fastapi import APIRouter

from src.agents.orchestrator import AgentOrchestrator
from src.web.schemas import APIResponse, ReportRequest

router = APIRouter(tags=["report"])
orchestrator = AgentOrchestrator()


@router.post("/report", response_model=APIResponse)
def report(payload: ReportRequest) -> APIResponse:
    result = orchestrator.run_report(payload.query, payload.protocol)
    return APIResponse(success=True, data=result)
