"""
Text-to-Speech service.
"""

from __future__ import annotations

from app.ai.tts.base import BaseTTS
from app.ai.tts.factory import create_tts
from app.ai.tts.schemas import TTSRequest, TTSResponse
from app.core.logging import get_logger


logger = get_logger(__name__)


class TTSService:
    """
    Application service for text-to-speech generation.

    Keeps the rest of the application independent
    from the underlying TTS provider.
    """

    def __init__(
        self,
        provider: BaseTTS | None = None,
    ) -> None:
        self._provider = (
            provider
            if provider is not None
            else create_tts()
        )

    async def synthesize(
        self,
        request: TTSRequest,
    ) -> TTSResponse:
        """
        Convert text into speech using the configured provider.
        """

        logger.info(
            "TTS service synthesizing text: %r",
            request.text,
        )

        response = await self._provider.synthesize(request)

        logger.info(
            "TTS service generated audio using model: %s",
            response.model,
        )

        return response