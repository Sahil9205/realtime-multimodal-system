"""
Tests for the information request handler.
"""

from app.conversation.handlers.information import (
    InformationRequestHandler,
)
from app.conversation.schemas.conversation_input import ConversationInput


def test_information_handler_returns_response() -> None:
    handler = InformationRequestHandler()

    conversation_input = ConversationInput(
        text="What is RAG?",
        confidence=0.94,
    )

    response = handler.handle(conversation_input)

    assert response.text == (
        "I can help you find information about that. "
        "The information system is not connected yet."
    )