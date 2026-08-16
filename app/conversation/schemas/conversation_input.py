"""
Input schema for the conversation engine.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ConversationInput(BaseModel):
    """
    Represents an input received by the conversation engine.
    """

    text: str = Field(
        ...,
        min_length=1,
        description="User's utterance text.",
    )

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence of the upstream ASR result.",
    )

    model_config = ConfigDict(frozen=True)