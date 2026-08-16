"""
Schemas for Text-to-Speech providers.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TTSRequest(BaseModel):
    """
    Represents a text-to-speech request.
    """

    text: str = Field(
        ...,
        min_length=1,
        description="Text to convert into speech.",
    )

    voice: str | None = Field(
        default=None,
        description="Voice identifier used by the provider.",
    )

    language: str = Field(
        default="en",
        min_length=2,
        description="Language of the spoken text.",
    )

    model: str | None = Field(
        default=None,
        description="TTS model identifier.",
    )

    model_config = ConfigDict(frozen=True)


class TTSResponse(BaseModel):
    """
    Represents generated speech audio.
    """

    audio: bytes = Field(
        ...,
        min_length=1,
        description="Generated audio bytes.",
    )

    content_type: str = Field(
        default="audio/wav",
        min_length=1,
        description="MIME type of the generated audio.",
    )

    model: str | None = Field(
        default=None,
        description="TTS model used for generation.",
    )

    duration_seconds: float | None = Field(
        default=None,
        ge=0.0,
        description="Duration of generated audio.",
    )

    model_config = ConfigDict(frozen=True)