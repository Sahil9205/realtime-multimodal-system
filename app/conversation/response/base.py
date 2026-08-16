"""
Base interface for conversation response generation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.conversation.schemas.conversation_output import ConversationOutput


class BaseResponseBuilder(ABC):
    """
    Abstract interface for building conversation responses.
    """

    @abstractmethod
    def build(self, text: str) -> ConversationOutput:
        """
        Build a standardized conversation response.

        Args:
            text: Response text.

        Returns:
            ConversationOutput.
        """
        raise NotImplementedError