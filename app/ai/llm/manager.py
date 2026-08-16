"""
LLM manager.
"""

from __future__ import annotations

from app.ai.llm.base import BaseLLM
from app.ai.llm.schemas import LLMRequest, LLMResponse
from app.ai.llm.factory import create_llm
from app.core.logging import get_logger


logger = get_logger(__name__)


class LLMManager:
    """
    Manages interaction with the configured LLM provider.
    """

    def __init__(
        self,
        llm: BaseLLM | None = None,
    ) -> None:
        self._llm = (
            llm
            if llm is not None
            else create_llm()
        )

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        """
        Generate an LLM response using the configured provider.
        """

        logger.info(
            "Sending request to LLM provider: %s",
            self._llm.__class__.__name__,
        )

        response = await self._llm.generate(request)

        logger.info(
            "LLM response received: %r",
            response.content,
        )

        return response