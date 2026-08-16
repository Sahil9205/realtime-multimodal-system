"""
Conversation intent definitions.
"""

from enum import Enum


class Intent(str, Enum):
    """Supported conversation intents."""

    GREETING = "greeting"
    INFORMATION_REQUEST = "information_request"
    GENERAL_CONVERSATION = "general_conversation"