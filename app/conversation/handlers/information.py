"""
Handler for information requests.
"""

from __future__ import annotations

from app.conversation.handlers.base import BaseConversationHandler
from app.conversation.schemas.conversation_input import ConversationInput
from app.conversation.schemas.conversation_output import ConversationOutput
from app.core.logging import get_logger


logger = get_logger(__name__)


class InformationRequestHandler(BaseConversationHandler):
    """
    Handles information-request conversations.

    This is currently a placeholder handler.
    It will later connect to the RAG/LLM pipeline.
    """

    def handle(
        self,
        conversation_input: ConversationInput,
    ) -> ConversationOutput:
        """
        Process an information request.

        Args:
            conversation_input: User conversation input.

        Returns:
            Conversation response.
        """

        logger.info(
            "Handling information request: %r",
            conversation_input.text,
        )

        return ConversationOutput(
            text=(
                "I can help you find information about that. "
                "The information system is not connected yet. "
                f"You asked: {conversation_input.text}"
            ),
        )