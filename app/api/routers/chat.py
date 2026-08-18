"""Chat router."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas.chat_request import ChatRequest
from app.api.schemas.chat_response import ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(
        response=f"Echo: {request.message}",
        success=True,
    )
