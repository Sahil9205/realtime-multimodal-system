"""
Conversation intent router.
"""

from __future__ import annotations

from app.conversation.handlers.base import BaseConversationHandler
from app.conversation.handlers.information import InformationRequestHandler
from app.conversation.schemas.conversation_input import ConversationInput
from app.conversation.schemas.conversation_output import ConversationOutput
from app.conversation.schemas.intent import Intent
from app.core.logging import get_logger


logger = get_logger(__name__)


class IntentRouter:
    """
    Routes conversation intents to their corresponding handlers.
    """

    def __init__(
        self,
        greeting_handler: BaseConversationHandler,
        information_handler: BaseConversationHandler,
        general_handler: BaseConversationHandler,
    ) -> None:

        self._handlers = {
            Intent.GREETING: greeting_handler,
            Intent.INFORMATION_REQUEST: information_handler,
            Intent.GENERAL_CONVERSATION: general_handler,
        }

    def route(
        self,
        intent: Intent,
        conversation_input: ConversationInput,
    ) -> ConversationOutput:
        """
        Route a conversation input to the appropriate handler.
        """

        handler = self._handlers.get(
            intent,
            self._handlers[Intent.GENERAL_CONVERSATION],
        )

        logger.info(
            "Intent routed: intent=%s handler=%s",
            intent.value,
            handler.__class__.__name__,
        )

        return handler.handle(conversation_input)