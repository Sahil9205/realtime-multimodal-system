"""Chat response schema."""

from pydantic import BaseModel


class ChatResponse(BaseModel):
    response: str
    success: bool = True
