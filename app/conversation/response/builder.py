"""
Conversation response builder.
"""

from __future__ import annotations

from app.conversation.response.base import BaseResponseBuilder
from app.conversation.schemas.conversation_output import ConversationOutput
from app.core.logging import get_logger


logger = get_logger(__name__)


class ResponseBuilder(BaseResponseBuilder):
    """
    Builds standardized conversation responses.
    """

    def build(self, text: str) -> ConversationOutput:
        """
        Build a conversation response.

        Args:
            text: Response text.

        Returns:
            ConversationOutput.
        """

        normalized_text = text.strip()

        if not normalized_text:
            normalized_text = (
            "I'm sorry, I wasn't able to generate a response."
        )

        response = ConversationOutput(
            text=normalized_text,
        )

        logger.info(
            "Conversation response built: %r",
            response.text,
        )

        return response