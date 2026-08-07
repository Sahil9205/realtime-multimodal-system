"""
Audio schemas.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AudioChunk(BaseModel):
    """
    Represents a chunk of audio data.
    """

    data: bytes = Field(
        ...,
        description="Raw PCM audio bytes.",
    )

    sample_rate: int = Field(
        ...,
        gt=0,
        description="Audio sample rate in Hz.",
    )

    channels: int = Field(
        ...,
        gt=0,
        description="Number of audio channels.",
    )

    timestamp: float = Field(
        ...,
        ge=0,
        description="Chunk timestamp in seconds.",
    )

    model_config = ConfigDict(frozen=True)