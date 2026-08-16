"""
Base interface for conversation handlers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.conversation.schemas.conversation_input import ConversationInput
from app.conversation.schemas.conversation_output import ConversationOutput


class BaseConversationHandler(ABC):
    """
    Abstract interface for conversation intent handlers.

    Each concrete handler is responsible for processing a specific
    type of conversation input.
    """

    @abstractmethod
    def handle(
        self,
        conversation_input: ConversationInput,
    ) -> ConversationOutput:
        """
        Process a conversation input.

        Args:
            conversation_input: Normalized user conversation input.

        Returns:
            Conversation response.
        """
        raise NotImplementedError