"""
Pipecat processor bridging conversation responses with TTS.
"""

from __future__ import annotations

from pipecat.frames.frames import OutputAudioRawFrame
from pipecat.processors.frame_processor import (
    FrameDirection,
    FrameProcessor,
)

from app.ai.tts.schemas import TTSRequest
from app.ai.tts.service import TTSService
from app.realtime.frames.conversation import ConversationResponseFrame
from app.core.logging import get_logger


logger = get_logger(__name__)


class TTSProcessor(FrameProcessor):
    """
    Converts ConversationResponseFrame objects into
    synthesized Pipecat audio frames.

    Pipeline:

        ConversationResponseFrame
            ↓
        TTSService
            ↓
        TTSResponse
            ↓
        OutputAudioRawFrame
    """

    def __init__(
        self,
        tts_service: TTSService | None = None,
    ) -> None:
        super().__init__()

        self._tts_service = (
            tts_service
            if tts_service is not None
            else TTSService()
        )

        self._sample_rate = 24000
        self._num_channels = 1

    async def process_frame(
        self,
        frame,
        direction: FrameDirection,
    ) -> None:
        """
        Process incoming Pipecat frames.

        Only ConversationResponseFrame instances are sent
        to the TTS service. Other frames continue downstream.
        """

        if not isinstance(
            frame,
            ConversationResponseFrame,
        ):
            await self.push_frame(
                frame,
                direction,
            )
            return

        text = frame.text.strip()

        if not text:
            logger.debug(
                "Ignoring empty ConversationResponseFrame."
            )
            return

        logger.info(
            "TTSProcessor received response: %r",
            text,
        )

        request = TTSRequest(
            text=text,
            language="en",
        )

        try:
            response = await self._tts_service.synthesize(
                request
            )

            logger.info(
                "TTS generated %d audio bytes using model=%s",
                len(response.audio),
                response.model,
            )

            audio_frame = OutputAudioRawFrame(
                audio=response.audio,
                sample_rate=self._sample_rate,
                num_channels=self._num_channels,
            )

            await self.push_frame(
                audio_frame,
                FrameDirection.DOWNSTREAM,
            )

        except Exception:
            logger.exception(
                "TTS synthesis failed for response: %r",
                text,
            )
            raise