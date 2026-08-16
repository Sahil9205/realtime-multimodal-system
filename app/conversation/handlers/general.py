"""
Handler for general conversation.
"""

from __future__ import annotations

from app.conversation.handlers.base import BaseConversationHandler
from app.conversation.schemas.conversation_input import ConversationInput
from app.conversation.schemas.conversation_output import ConversationOutput
from app.core.logging import get_logger


logger = get_logger(__name__)


class GeneralConversationHandler(BaseConversationHandler):
    """
    Handles general conversational inputs.
    """

    def handle(
        self,
        conversation_input: ConversationInput,
    ) -> ConversationOutput:
        """
        Generate a response for general conversation.

        Args:
            conversation_input: User conversation input.

        Returns:
            Conversation response.
        """

        logger.info(
            "Handling general conversation: %r",
            conversation_input.text,
        )

        return ConversationOutput(
            text=f"You said: {conversation_input.text}",
        )