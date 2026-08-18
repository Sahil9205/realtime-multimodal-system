"""
Voice pipeline orchestration.

Connects the streaming ASR provider with the
utterance manager and conversation engine.
"""

from __future__ import annotations

from app.ai.asr.base import BaseASR
from app.ai.asr.schemas import TranscriptionResult
from app.ai.asr.utterance_manager import UtteranceManager
from app.conversation.engine import ConversationEngine
from app.conversation.schemas.conversation_output import ConversationOutput
from app.core.logging import get_logger


logger = get_logger(__name__)


class VoicePipeline:
    """
    Orchestrates the voice pipeline from streaming ASR
    transcription to conversation processing.
    """

    def __init__(
        self,
        asr: BaseASR,
        utterance_manager: UtteranceManager | None = None,
        conversation_engine: ConversationEngine | None = None,
    ) -> None:
        self._asr = asr

        self._utterance_manager = (
            utterance_manager
            if utterance_manager is not None
            else UtteranceManager()
        )

        self._conversation_engine = (
            conversation_engine
            if conversation_engine is not None
            else ConversationEngine()
        )

    async def start(self) -> None:
        """
        Start the voice pipeline.

        Establishes the ASR connection.
        """
        logger.info("Starting voice pipeline.")

        await self._asr.connect()

        logger.info("Voice pipeline started.")

    async def stop(self) -> None:
        """
        Stop the voice pipeline.

        Closes the ASR connection.
        """
        logger.info("Stopping voice pipeline.")

        await self._asr.disconnect()

        logger.info("Voice pipeline stopped.")

    async def process_next(
        self,
    ) -> ConversationOutput | None:
        """
        Process the next transcription result.

        Pipeline:

            ASR
            ↓
            TranscriptionResult
            ↓
            UtteranceManager
            ↓
            UserUtterance
            ↓
            ConversationEngine
            ↓
            ConversationOutput

        Returns:
            ConversationOutput when a complete user utterance
            has been processed, otherwise None.
        """

        transcription: TranscriptionResult = (
            await self._asr.receive_transcript()
        )

        logger.debug(
            "Received transcription: %r | final=%s | speech_final=%s",
            transcription.transcript,
            transcription.is_final,
            transcription.speech_final,
        )

        utterance = self._utterance_manager.process(
            transcription
        )

        if utterance is None:
            return None

        logger.info(
            "Voice pipeline produced utterance: %r",
            utterance.text,
        )

        result = self._conversation_engine.process(utterance)
        if hasattr(result, "__await__"):
            conversation_output = await result
        else:
            conversation_output = result

        logger.info(
            "Conversation engine produced response: %r",
            conversation_output.text,
        )

        return conversation_output