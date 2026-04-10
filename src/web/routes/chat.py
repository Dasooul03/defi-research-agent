from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.agents.orchestrator import AgentOrchestrator
from src.web.schemas import APIResponse, ChatRequest

router = APIRouter(tags=["chat"])
orchestrator = AgentOrchestrator()


@router.post("/chat", response_model=APIResponse)
def chat(payload: ChatRequest) -> APIResponse:
    try:
        result = orchestrator.run_chat(payload.query)
        return APIResponse(success=True, data=result)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/chat/stream")
async def chat_stream(payload: ChatRequest) -> StreamingResponse:
    async def event_generator():
        try:
            for token in orchestrator.stream_chat(payload.query):
                event_data = json.dumps({"type": "chunk", "content": token}, ensure_ascii=False)
                yield f"data: {event_data}\n\n"
                await asyncio.sleep(0)

            yield "data: {\"type\":\"done\"}\n\n"
        except Exception as exc:  # pragma: no cover
            err = json.dumps({"type": "error", "message": str(exc)}, ensure_ascii=False)
            yield f"data: {err}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
