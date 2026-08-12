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
    Captures continuous audio from the system microphone.
    """

    def __init__(self) -> None:
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = settings.CHUNK_SIZE
        self.device = settings.AUDIO_INPUT_DEVICE

        self._stream: sd.InputStream | None = None
        self._queue: list[bytes] = []

        logger.info(
            "Microphone initialized: device=%s, sample_rate=%s, channels=%s",
            self.device,
            self.sample_rate,
            self.channels,
        )

    def _callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info,
        status,
    ) -> None:
        """
        Called continuously by sounddevice whenever audio arrives.
        """

        if status:
            logger.warning(
                "Microphone stream status: %s",
                status,
            )

        audio = indata.copy()

        logger.debug(
            "Microphone audio: shape=%s dtype=%s min=%d max=%d mean=%.2f",
            audio.shape,
            audio.dtype,
            audio.min(),
            audio.max(),
            audio.mean(),
        )

        self._queue.append(audio.tobytes())

    def start(self) -> None:
        """
        Start continuous microphone capture.
        """

        if self._stream is not None:
            return

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            blocksize=self.chunk_size,
            device=self.device,
            callback=self._callback,
        )

        self._stream.start()

        logger.info(
            "Microphone stream started: device=%s",
            self.device,
        )

    def read(self) -> AudioChunk:
        """
        Read the next available audio chunk.
        """

        if self._stream is None:
            raise RuntimeError(
                "Microphone stream has not been started."
            )

        while not self._queue:
            time.sleep(0.005)

        data = self._queue.pop(0)

        return AudioChunk(
            data=data,
            sample_rate=self.sample_rate,
            channels=self.channels,
            timestamp=time.perf_counter(),
        )

    def close(self) -> None:
        """
        Stop and release microphone resources.
        """

        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        self._queue.clear()

        logger.info(
            "Microphone stopped. device=%s",
            self.device,
        )