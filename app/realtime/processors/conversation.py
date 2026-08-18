"""
Pipecat processor bridging ASR transcription with the conversation engine.
"""

from __future__ import annotations

from pipecat.frames.frames import TranscriptionFrame
from pipecat.processors.frame_processor import (
    FrameDirection,
    FrameProcessor,
)
from app.realtime.frames.conversation import ConversationResponseFrame
from app.ai.asr.schemas import UserUtterance
from app.conversation.engine import ConversationEngine
from app.core.logging import get_logger


logger = get_logger(__name__)


class ConversationProcessor(FrameProcessor):
    """
    Bridges finalized ASR transcription frames with the
    application conversation engine.

    Responsibilities:

        TranscriptionFrame
            ↓
        UserUtterance
            ↓
        ConversationEngine
            ↓
        ConversationOutput
    """

    def __init__(
        self,
        conversation_engine: ConversationEngine | None = None,
    ) -> None:
        super().__init__()

        self._conversation_engine = (
            conversation_engine
            if conversation_engine is not None
            else ConversationEngine()
        )

    async def process_frame(
        self,
        frame,
        direction: FrameDirection,
    ) -> None:
        """
        Process incoming Pipecat frames.

        Only finalized TranscriptionFrame instances are sent
        to the conversation engine. All other frames continue
        downstream unchanged.
        """

        if not isinstance(frame, TranscriptionFrame):
            await self.push_frame(
                frame,
                direction,
            )
            return

        # Ignore empty transcription frames.
        text = frame.text.strip()

        if not text:
            logger.debug(
                "Ignoring empty transcription frame."
            )

            return

        # Only finalized ASR results should enter the
        # conversation layer.
        if not frame.finalized:
            logger.debug(
                "Ignoring non-final transcription: %r",
                text,
            )

            return

        logger.info(
            "Received finalized transcription: %r",
            text,
        )

        utterance = UserUtterance(
            text=text,
            confidence=None,
        )

        try:
            response = await self._conversation_engine.process(
                utterance
            )

            logger.info(
                "Conversation response generated: %r",
                response.text,
            )

            await self.push_frame(
                ConversationResponseFrame(
                    text=response.text,
                ),
                FrameDirection.DOWNSTREAM,
            )

        except Exception:
            logger.exception(
                "Error while processing conversation input: %r",
                text,
            )

            raise