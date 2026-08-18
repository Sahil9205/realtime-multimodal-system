"""Conversation router."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas.conversation_request import ConversationRequest
from app.api.schemas.conversation_response import ConversationResponse

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse)
async def create_conversation(request: ConversationRequest) -> ConversationResponse:
    return ConversationResponse(
        conversation_id="demo-conversation",
        message=f"Received: {request.message}",
    )
