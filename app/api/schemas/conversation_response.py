"""Conversation response schema."""

from pydantic import BaseModel


class ConversationResponse(BaseModel):
    conversation_id: str
    message: str
