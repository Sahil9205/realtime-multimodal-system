"""
Conversation response manager.
"""

from __future__ import annotations

from app.conversation.response.builder import ResponseBuilder
from app.conversation.schemas.conversation_output import ConversationOutput
from app.core.logging import get_logger


logger = get_logger(__name__)


class ResponseManager:
    """
    Manages the creation of standardized conversation responses.

    The manager acts as the orchestration layer above
    ResponseBuilder and provides a single entry point
    for producing ConversationOutput objects.
    """

    def __init__(
        self,
        builder: ResponseBuilder | None = None,
    ) -> None:
        self._builder = (
            builder
            if builder is not None
            else ResponseBuilder()
        )

    def create(self, text: str) -> ConversationOutput:
        """
        Create a standardized conversation response.

        Args:
            text: Raw response text.

        Returns:
            ConversationOutput.
        """

        logger.info(
            "Creating conversation response."
        )

        response = self._builder.build(text)

        logger.info(
            "Conversation response created: %r",
            response.text,
        )

        return response