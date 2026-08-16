"""
System audio output implementation.
"""

from __future__ import annotations

import io

from pydub import AudioSegment
import sounddevice as sd

from app.ai.tts.schemas import TTSResponse
from app.audio.output.base import BaseAudioOutput
from app.core.logging import get_logger


logger = get_logger(__name__)


class SystemAudioOutput(BaseAudioOutput):
    """
    Plays generated TTS audio through the system speaker.
    """

    async def play(
        self,
        response: TTSResponse,
    ) -> None:
        """
        Decode TTS audio and play it through the system speaker.
        """

        if not response.audio:
            raise ValueError("Audio data cannot be empty.")

        logger.info(
            "Playing audio output: %d bytes",
            len(response.audio),
        )

        audio = AudioSegment.from_file(
            io.BytesIO(response.audio),
            format="mp3",
        )

        samples = audio.get_array_of_samples()

        sd.play(
            samples,
            samplerate=audio.frame_rate,
            blocking=True,
        )

        sd.stop()

        logger.info("Audio playback completed.")