"""Conversation request schema."""

from pydantic import BaseModel, Field


class ConversationRequest(BaseModel):
    message: str = Field(..., min_length=1)
    user_id: str | None = None
