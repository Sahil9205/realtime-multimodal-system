"""
Hugging Face LLM provider.
"""

from __future__ import annotations

from app.ai.llm.base import BaseLLM
from app.ai.llm.schemas import LLMRequest, LLMResponse
from app.core.logging import get_logger


logger = get_logger(__name__)


class HuggingFaceLLM(BaseLLM):
    """
    Hugging Face implementation of the LLM provider.

    Model initialization/inference will be connected later.
    """

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a response from the Hugging Face model.

        Currently a deterministic placeholder so the provider
        contract can be tested without downloading a model.
        """

        user_message = request.messages[-1].content

        logger.info(
            "Generating LLM response for: %r",
            user_message,
        )

        return LLMResponse(
            content=f"LLM response to: {user_message}",
            model="huggingface",
            finish_reason="stop",
        )