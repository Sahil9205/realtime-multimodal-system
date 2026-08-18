"""
Streaming text-to-speech support for real-time audio generation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncGenerator

from app.ai.tts.schemas import TTSRequest, TTSResponse
from app.core.logging import get_logger


logger = get_logger(__name__)


class StreamingTTSResponse:
    """
    Represents a streaming TTS response with audio chunks.
    """

    def __init__(self) -> None:
        """Initialize streaming response."""
        self.chunks: list[bytes] = []
        self.is_complete = False
        self.content_type = "audio/mpeg"
        self.model = "unknown"

    def add_chunk(self, chunk: bytes) -> None:
        """
        Add an audio chunk.

        Args:
            chunk: Audio bytes chunk.
        """
        if chunk:
            self.chunks.append(chunk)

    def complete(self) -> None:
        """Mark response as complete."""
        self.is_complete = True

    def get_full_audio(self) -> bytes:
        """
        Get concatenated audio from all chunks.

        Returns:
            Complete audio bytes.
        """
        return b"".join(self.chunks)


class BaseStreamingTTS(ABC):
    """
    Abstract interface for streaming TTS providers.
    
    Streaming TTS allows audio to be generated and played in real-time
    without waiting for the complete response.
    """

    @abstractmethod
    async def synthesize_streaming(
        self,
        request: TTSRequest,
    ) -> AsyncGenerator[bytes, None]:
        """
        Generate speech as a stream of audio chunks.

        Args:
            request: TTS request.

        Yields:
            Audio chunks as they're generated.
        """
        raise NotImplementedError

    @abstractmethod
    async def synthesize(
        self,
        request: TTSRequest,
    ) -> TTSResponse:
        """
        Generate complete speech (fallback to non-streaming).

        Args:
            request: TTS request.

        Returns:
            Complete audio response.
        """
        raise NotImplementedError


class StreamingTTSService:
    """
    Service for streaming TTS generation.
    """

    def __init__(self, provider: BaseStreamingTTS | None = None) -> None:
        """
        Initialize streaming TTS service.

        Args:
            provider: Streaming TTS provider instance.
        """
        self._provider = provider
        logger.info("StreamingTTSService initialized.")

    async def synthesize_streaming(
        self,
        text: str,
        voice: str | None = None,
    ) -> AsyncGenerator[bytes, None]:
        """
        Generate speech as a stream of audio chunks.

        Args:
            text: Text to synthesize.
            voice: Optional voice identifier.

        Yields:
            Audio chunks as they're generated.
        """
        if self._provider is None:
            logger.error("No streaming TTS provider configured.")
            return

        request = TTSRequest(
            text=text,
            voice=voice,
        )

        logger.info(
            "Starting streaming TTS for text: %r",
            text[:50],
        )

        async for chunk in self._provider.synthesize_streaming(request):
            yield chunk

        logger.info("Streaming TTS completed.")

    async def synthesize(
        self,
        text: str,
        voice: str | None = None,
    ) -> TTSResponse:
        """
        Generate complete speech (non-streaming fallback).

        Args:
            text: Text to synthesize.
            voice: Optional voice identifier.

        Returns:
            Complete audio response.
        """
        if self._provider is None:
            logger.error("No streaming TTS provider configured.")
            raise RuntimeError("No TTS provider configured.")

        request = TTSRequest(
            text=text,
            voice=voice,
        )

        logger.info(
            "Starting TTS for text: %r",
            text[:50],
        )

        response = await self._provider.synthesize(request)

        logger.info(
            "TTS synthesis completed using model: %s",
            response.model,
        )

        return response
