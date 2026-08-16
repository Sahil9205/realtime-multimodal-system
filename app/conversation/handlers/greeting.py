"""
Handler for greeting conversations.
"""

from __future__ import annotations

from app.conversation.handlers.base import BaseConversationHandler
from app.conversation.schemas.conversation_input import ConversationInput
from app.conversation.schemas.conversation_output import ConversationOutput
from app.core.logging import get_logger


logger = get_logger(__name__)


class GreetingHandler(BaseConversationHandler):
    """
    Handles greeting-type conversation inputs.
    """

    def handle(
        self,
        conversation_input: ConversationInput,
    ) -> ConversationOutput:
        """
        Generate a response to a greeting.

        Args:
            conversation_input: User conversation input.

        Returns:
            Conversation response.
        """

        logger.info(
            "Handling greeting: %r",
            conversation_input.text,
        )

        return ConversationOutput(
            text="Hello! How can I help you?",
        )