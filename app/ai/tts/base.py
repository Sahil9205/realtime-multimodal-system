"""
Base interface for Text-to-Speech providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.tts.schemas import TTSRequest, TTSResponse


class BaseTTS(ABC):
    """
    Abstract interface for TTS providers.
    """

    @abstractmethod
    async def synthesize(
        self,
        request: TTSRequest,
    ) -> TTSResponse:
        """
        Convert text into speech.

        Args:
            request: Structured TTS request.

        Returns:
            Generated audio response.
        """
        raise NotImplementedError