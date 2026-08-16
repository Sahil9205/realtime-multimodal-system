"""
Voice response orchestration service.
"""

from __future__ import annotations

from app.ai.tts.schemas import TTSRequest
from app.ai.tts.service import TTSService
from app.audio.output.base import BaseAudioOutput
from app.audio.output.system import SystemAudioOutput
from app.conversation.schemas.conversation_output import ConversationOutput
from app.core.logging import get_logger


logger = get_logger(__name__)


class VoiceResponseService:
    """
    Coordinates conversation responses with TTS and audio output.

    Flow:

        ConversationOutput
            ↓
        TTSRequest
            ↓
        TTSService
            ↓
        TTSResponse
            ↓
        AudioOutput
    """

    def __init__(
        self,
        tts_service: TTSService | None = None,
        audio_output: BaseAudioOutput | None = None,
    ) -> None:
        self._tts_service = (
            tts_service
            if tts_service is not None
            else TTSService()
        )

        self._audio_output = (
            audio_output
            if audio_output is not None
            else SystemAudioOutput()
        )

    async def respond(
        self,
        response: ConversationOutput,
    ) -> None:
        """
        Convert a conversation response into speech
        and play it through the configured audio output.
        """

        logger.info(
            "Preparing voice response: %r",
            response.text,
        )

        tts_request = TTSRequest(
            text=response.text,
        )

        tts_response = await self._tts_service.synthesize(
            tts_request,
        )

        await self._audio_output.play(
            tts_response,
        )

        logger.info("Voice response playback completed.")