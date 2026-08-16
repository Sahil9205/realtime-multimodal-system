"""
Conversation intent classifier.
"""

from __future__ import annotations

from app.conversation.schemas.intent import Intent
from app.core.logging import get_logger


logger = get_logger(__name__)


class IntentClassifier:
    """
    Classifies a user message into a conversation intent.

    This is currently a deterministic baseline classifier.
    It can later be replaced with an LLM-based classifier
    without changing the ConversationEngine interface.
    """

    def classify(self, text: str) -> Intent:
        """
        Classify user input.

        Args:
            text: User's utterance.

        Returns:
            Detected Intent.
        """

        normalized_text = text.strip().lower()

        if not normalized_text:
            return Intent.GENERAL_CONVERSATION

        if self._is_greeting(normalized_text):
            intent = Intent.GREETING

        elif self._is_information_request(normalized_text):
            intent = Intent.INFORMATION_REQUEST

        else:
            intent = Intent.GENERAL_CONVERSATION

        logger.info(
            "Intent classified: text=%r intent=%s",
            text,
            intent.value,
        )

        return intent

    @staticmethod
    def _is_greeting(text: str) -> bool:
        """Check whether the text is a greeting."""

        greetings = {
            "hello",
            "hi",
            "hey",
            "hey alisha",
            "hello alisha",
            "hi alisha",
        }

        return text in greetings

    @staticmethod
    def _is_information_request(text: str) -> bool:
        """Check whether the text looks like an information request."""

        question_starters = (
            "what ",
            "what's ",
            "who ",
            "when ",
            "where ",
            "why ",
            "which ",
            "can you tell me ",
        )

        return text.startswith(question_starters)