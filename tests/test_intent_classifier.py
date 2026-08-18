"""
Tests for the conversation intent classifier.
"""

from app.conversation.intent.classifier import IntentClassifier
from app.conversation.schemas.intent import Intent


def test_greeting_is_classified_correctly() -> None:
    classifier = IntentClassifier()

    intent = classifier.classify("Hello Alisha")

    assert intent == Intent.GREETING


def test_information_request_is_classified_correctly() -> None:
    classifier = IntentClassifier()

    intent = classifier.classify(
        "What is the leave policy?"
    )

    assert intent == Intent.INFORMATION_REQUEST


def test_general_conversation_is_classified_correctly() -> None:
    classifier = IntentClassifier()

    intent = classifier.classify(
        "How are you?"
    )

    assert intent == Intent.GENERAL_CONVERSATION


def test_unknown_input_falls_back_to_general_conversation() -> None:
    classifier = IntentClassifier()

    intent = classifier.classify(
        "asdfghjkl"
    )

    assert intent == Intent.GENERAL_CONVERSATION