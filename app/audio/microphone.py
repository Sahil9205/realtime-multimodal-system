"""
Microphone audio capture.
"""

from __future__ import annotations

import time

import numpy as np
import sounddevice as sd

from app.audio.schemas import AudioChunk
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Microphone:
    """
    Captures audio from the system microphone.
    """

    def __init__(self) -> None:
        self.sample_rate = settings.SAMPLE_RATE
        self.channels = settings.CHANNELS
        self.chunk_size = settings.CHUNK_SIZE

    def read(self) -> AudioChunk:
        """
        Capture a single chunk of audio.

        Returns:
            AudioChunk containing PCM audio.
        """
        audio = sd.rec(
            frames=self.chunk_size,
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
        )

        sd.wait()

        return AudioChunk(
            data=audio.tobytes(),
            sample_rate=self.sample_rate,
            channels=self.channels,
            timestamp=time.perf_counter(),
        )

    def close(self) -> None:
        """
        Release microphone resources.
        """
        sd.stop()
        logger.info("Microphone stopped.")