"""
Base interface for Large Language Model (LLM) providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.llm.schemas import LLMRequest, LLMResponse


class BaseLLM(ABC):
    """
    Abstract interface for LLM providers.
    """

    @abstractmethod
    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            request: Structured LLM request.

        Returns:
            Generated LLM response.
        """
        raise NotImplementedError