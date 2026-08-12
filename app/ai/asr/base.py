"""
Base interface for Automatic Speech Recognition (ASR) providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.asr.schemas import TranscriptionResult


class BaseASR(ABC):
    """
    Abstract interface for streaming ASR providers.
    """

    @abstractmethod
    async def connect(self) -> None:
        """
        Establish a connection with the ASR provider.
        """
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Close the connection with the ASR provider.
        """
        raise NotImplementedError

    @abstractmethod
    async def send_audio(
        self,
        audio: bytes,
    ) -> None:
        """
        Send an audio chunk to the ASR provider.

        Args:
            audio: Raw audio bytes.
        """
        raise NotImplementedError

    @abstractmethod
    async def receive_transcript(
        self,
    ) -> TranscriptionResult:
        """
        Receive the next transcription result.

        Returns:
            TranscriptionResult from the ASR provider.
        """
        raise NotImplementedError