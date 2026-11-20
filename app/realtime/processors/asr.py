"""
Pipecat processor bridging real-time audio with the ASR layer.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from pipecat.frames.frames import InputAudioRawFrame, TranscriptionFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from app.ai.asr.base import BaseASR
from app.ai.asr.utterance_manager import UtteranceManager
from app.core.logging import get_logger


logger = get_logger(__name__)


class ASRProcessor(FrameProcessor):
    """
    Bridges Pipecat audio frames with the application's ASR layer.

    Responsibilities:
        InputAudioRawFrame
            ↓
        BaseASR.send_audio()
            ↓
        TranscriptionResult
            ↓
        UtteranceManager
            ↓
        TranscriptionFrame
    """

    def __init__(
        self,
        asr: BaseASR,
        utterance_manager: UtteranceManager | None = None,
    ) -> None:
        super().__init__()

        self._asr = asr
        self._utterance_manager = (
            utterance_manager
            if utterance_manager is not None
            else UtteranceManager()
        )

        self._receive_task: asyncio.Task | None = None
        self._finalize_requested = False

    async def start(self) -> None:
        """
        Start the ASR provider and transcript listener.
        """

        logger.info("Starting ASR processor.")

        await self._asr.connect()

        self._receive_task = asyncio.create_task(
            self._receive_transcripts()
        )

        logger.info("ASR processor started.")

    async def stop(self) -> None:
        """
        Stop the transcript listener and disconnect ASR.
        """

        logger.info("Stopping ASR processor.")

        if self._receive_task is not None:
            self._receive_task.cancel()

            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

            self._receive_task = None

        await self._asr.disconnect()

        logger.info("ASR processor stopped.")

    async def finalize(self) -> None:
        """Flush the current provider-side speech segment without disconnecting."""
        self._finalize_requested = True
        await self._asr.finalize()

    async def process_frame(
        self,
        frame,
        direction: FrameDirection,
    ) -> None:
        """
        Process incoming Pipecat frames.
        """

        if isinstance(frame, InputAudioRawFrame):
            await self._asr.send_audio(frame.audio)

            logger.debug(
                "Audio frame sent to ASR: %d bytes",
                len(frame.audio),
            )

        await self.push_frame(
            frame,
            direction,
        )

    async def _receive_transcripts(self) -> None:
        """
        Continuously receive transcripts from the ASR provider.
        """

        while True:
            try:
                result = await self._asr.receive_transcript()

                utterance = self._utterance_manager.process(
                    result,
                    force_finalize=self._finalize_requested and result.is_final,
                )

                if utterance is not None:
                    self._finalize_requested = False

                if utterance is None:
                    continue

                frame = TranscriptionFrame(
                    text=utterance.text,
                    user_id="user",
                    timestamp=datetime.now(
                        timezone.utc
                    ).isoformat(),
                    finalized=True,
                )

                await self.push_frame(
                    frame,
                    FrameDirection.DOWNSTREAM,
                )

                logger.info(
                    "ASR utterance emitted: %r",
                    utterance.text,
                )

            except asyncio.CancelledError:
                raise

            except Exception:
                logger.exception(
                    "Error while receiving ASR transcript."
                )