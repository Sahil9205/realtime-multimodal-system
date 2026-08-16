"""
Factory for creating LLM providers.
"""

from __future__ import annotations

from app.ai.llm.base import BaseLLM
from app.core.exceptions import LLMError
from app.core.logging import get_logger
from app.ai.llm.providers.huggingface import HuggingFaceLLM


logger = get_logger(__name__)


def create_llm() -> BaseLLM:
    """
    Create and return the configured LLM provider.

    Returns:
        Configured LLM provider.

    Raises:
        LLMError: If the configured provider is unsupported.
    """

    from app.core.config import settings

    provider = settings.LLM_PROVIDER.lower().strip()

    if provider == "huggingface":
        from app.ai.llm.providers.huggingface import HuggingFaceLLM

        logger.info(
            "Creating Hugging Face LLM provider."
        )

        return HuggingFaceLLM()

    raise LLMError(
        f"Unsupported LLM provider: {provider}"
    )