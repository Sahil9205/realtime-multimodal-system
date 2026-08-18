"""
Tests for conversation handlers.
"""

from app.conversation.handlers.greeting import GreetingHandler
from app.conversation.handlers.information import InformationRequestHandler
from app.conversation.handlers.general import GeneralConversationHandler
from app.conversation.schemas.conversation_input import ConversationInput


def test_greeting_handler_returns_response() -> None:
    handler = GreetingHandler()

    result = handler.handle(
        ConversationInput(text="Hello Alisha", confidence=0.95)
    )

    assert result.text == "Hello! How can I help you?"


def test_information_handler_returns_response() -> None:
    handler = InformationRequestHandler()

    result = handler.handle(
        ConversationInput(
            text="What is artificial intelligence?",
            confidence=0.90,
        )
    )

    assert "What is artificial intelligence?" in result.text


def test_general_conversation_handler_returns_response() -> None:
    handler = GeneralConversationHandler()

    result = handler.handle(
        ConversationInput(
            text="How are you?",
            confidence=0.85,
        )
    )

    assert result.text == "You said: How are you?"