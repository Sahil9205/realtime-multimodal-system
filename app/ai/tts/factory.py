"""
Factory for creating TTS providers.
"""

from __future__ import annotations

from app.ai.tts.base import BaseTTS
from app.core.exceptions import TTSError
from app.core.logging import get_logger


logger = get_logger(__name__)


def create_tts() -> BaseTTS:
    """
    Create the configured TTS provider.
    """

    from app.core.config import settings

    provider = settings.TTS_PROVIDER.lower().strip()

    if provider == "deepgram":
        from app.ai.tts.providers.deepgram import DeepgramTTS

        logger.info(
            "Creating Deepgram TTS provider."
        )

        return DeepgramTTS()

    raise TTSError(
        f"Unsupported TTS provider: {provider}"
    )