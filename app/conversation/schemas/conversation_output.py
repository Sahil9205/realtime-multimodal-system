"""
Output schema for the conversation engine.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ConversationOutput(BaseModel):
    """
    Represents the result produced by the conversation engine.
    """

    text: str = Field(
        ...,
        description="Response produced by the conversation engine.",
    )

    model_config = ConfigDict(frozen=True)