"""
Deepgram Text-to-Speech provider.
"""

from __future__ import annotations
import asyncio

from deepgram import DeepgramClient

from app.ai.tts.base import BaseTTS
from app.ai.tts.schemas import TTSRequest, TTSResponse
from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class DeepgramTTS(BaseTTS):
    """
    Deepgram implementation of the TTS provider.
    """

    def __init__(self) -> None:
        if not settings.DEEPGRAM_TTS_API_KEY:
            raise ValueError(
                "DEEPGRAM_TTS_API_KEY is not configured."
            )

        self._client = DeepgramClient(
            api_key=settings.DEEPGRAM_TTS_API_KEY,
        )

    async def synthesize(
        self,
        request: TTSRequest,
    ) -> TTSResponse:
        """
        Convert text into speech using Deepgram.
        """

        logger.info(
            "Generating speech with Deepgram: %r",
            request.text,
        )

        model = request.model or "aura-2-thalia-en"

        # Deepgram's SDK call is synchronous. Keeping it off the event loop
        # lets an interrupt reach the WebSocket manager immediately.
        response = await asyncio.to_thread(
            self._client.speak.v1.audio.generate,
            text=request.text,
            model=model,
        )

        if isinstance(response, (bytes, bytearray)):
            audio = bytes(response)
        elif hasattr(response, "stream"):
            audio = response.stream.getvalue()
        else:
            audio = b"".join(response)

        if not audio:
            raise RuntimeError(
                "Deepgram returned empty audio."
            )

        return TTSResponse(
            audio=audio,
            content_type="audio/mpeg",
            model=model,
        )
