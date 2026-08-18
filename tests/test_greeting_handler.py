"""
Tests for the greeting conversation handler.
"""

from app.conversation.handlers.greeting import GreetingHandler
from app.conversation.schemas.conversation_input import ConversationInput


def test_greeting_handler_returns_response() -> None:
    handler = GreetingHandler()

    conversation_input = ConversationInput(
        text="Hello Alisha",
        confidence=0.95,
    )

    response = handler.handle(conversation_input)

    assert response.text == "Hello! How can I help you?"