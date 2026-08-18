"""
Base interface for audio output.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.tts.schemas import TTSResponse


class BaseAudioOutput(ABC):
    """
    Abstract interface for system audio output.
    """

    @abstractmethod
    async def play(
        self,
        response: TTSResponse,
    ) -> None:
        """
        Play generated TTS audio.
        """
        raise NotImplementedError

    @abstractmethod
    async def interrupt(self) -> None:
        """
        Stop active playback immediately.
        """
        raise NotImplementedError