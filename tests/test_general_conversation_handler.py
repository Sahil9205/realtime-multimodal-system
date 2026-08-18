"""
Tests for the general conversation handler.
"""

from app.conversation.handlers.general import GeneralConversationHandler
from app.conversation.schemas.conversation_input import ConversationInput


def test_general_conversation_handler_returns_response() -> None:
    handler = GeneralConversationHandler()

    conversation_input = ConversationInput(
        text="How are you?",
        confidence=0.92,
    )

    response = handler.handle(conversation_input)

    assert response.text == "You said: How are you?"