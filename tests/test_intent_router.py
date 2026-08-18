"""
Tests for the conversation intent router.
"""

from app.conversation.handlers.general import GeneralConversationHandler
from app.conversation.handlers.greeting import GreetingHandler
from app.conversation.handlers.information import InformationRequestHandler
from app.conversation.intent.router import IntentRouter
from app.conversation.schemas.conversation_input import ConversationInput
from app.conversation.schemas.intent import Intent


def create_router() -> IntentRouter:
    return IntentRouter(
        greeting_handler=GreetingHandler(),
        information_handler=InformationRequestHandler(),
        general_handler=GeneralConversationHandler(),
    )


def test_greeting_routes_to_greeting_handler() -> None:
    router = create_router()

    conversation_input = ConversationInput(
        text="Hello Alisha",
        confidence=0.95,
    )

    response = router.route(
        Intent.GREETING,
        conversation_input,
    )

    assert response is not None
    assert "Hello" in response.text


def test_information_request_routes_to_information_handler() -> None:
    router = create_router()

    conversation_input = ConversationInput(
        text="What can you do?",
        confidence=0.90,
    )

    response = router.route(
        Intent.INFORMATION_REQUEST,
        conversation_input,
    )

    assert response is not None
    assert "What can you do?" in response.text


def test_general_conversation_routes_to_general_handler() -> None:
    router = create_router()

    conversation_input = ConversationInput(
        text="How are you?",
        confidence=0.90,
    )

    response = router.route(
        Intent.GENERAL_CONVERSATION,
        conversation_input,
    )

    assert response is not None