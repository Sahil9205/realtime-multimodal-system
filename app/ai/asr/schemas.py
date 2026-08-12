"""
Schemas for Automatic Speech Recognition (ASR).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TranscriptionResult(BaseModel):
    """
    Represents a transcription result from an ASR provider.
    """

    transcript: str = Field(
        ...,
        description="Recognized speech.",
    )

    is_final: bool = Field(
        default=False,
        description="Whether this transcript is final.",
    )

    speech_final: bool = Field(
        default=False,
        description="Whether the speaker's speech segment has ended.",
    )

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="ASR confidence score.",
    )

    model_config = ConfigDict(frozen=True)

class UserUtterance(BaseModel):
    """
    Represents one complete user speech turn.
    """

    text: str = Field(
        ...,
        min_length=1,
        description="Complete user utterance.",
    )

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence associated with the utterance.",
    )

    model_config = ConfigDict(frozen=True)