"""Chat API endpoints."""

from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.services.chat_service import run_chat, stream_chat

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("")
async def chat_info():
    """GET returns usage info. Chat requires POST with JSON body."""
    return {
        "endpoint": "/api/v1/chat",
        "method": "POST",
        "content_type": "application/json",
        "body_example": {
            "question": "Show top cardiologists in Bangalore",
            "session_id": None,
            "user_role": "analyst",
        },
        "stream_endpoint": "/api/v1/chat/stream",
        "docs": "/docs#/chat/chat_api_v1_chat_post",
        "note": "Opening this URL in a browser uses GET which only shows this help. Use POST to chat.",
    }


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None
    user_role: str = "analyst"


@router.post("")
async def chat(request: ChatRequest):
    """Synchronous chat — returns full agent pipeline result."""
    return await run_chat(request.question, request.session_id, request.user_role)


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """SSE streaming chat response."""

    async def event_generator():
        async for event in stream_chat(request.question, request.session_id):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
