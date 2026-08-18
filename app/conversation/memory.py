"""
Conversation memory for maintaining dialogue context.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.core.logging import get_logger


logger = get_logger(__name__)


class ConversationMessage(BaseModel):
    """
    Represents a single message in conversation history.
    """

    role: str = Field(
        ...,
        description="Role of the message sender (user|assistant).",
    )

    content: str = Field(
        ...,
        min_length=1,
        description="Message content.",
    )

    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the message was created.",
    )


class ConversationMemory:
    """
    Maintains conversation history for context-aware responses.
    
    Features:
    - Store user utterances and assistant responses
    - Retrieve recent conversation history
    - Manage memory size and lifetime
    - Clear memory on demand
    """

    def __init__(
        self,
        max_messages: int = 50,
        max_age_seconds: Optional[int] = 3600,
    ) -> None:
        """
        Initialize conversation memory.

        Args:
            max_messages: Maximum number of messages to store.
            max_age_seconds: Maximum age of messages in seconds (None = unlimited).
        """
        self._messages: list[ConversationMessage] = []
        self._max_messages = max_messages
        self._max_age_seconds = max_age_seconds

        logger.info(
            "ConversationMemory initialized with "
            "max_messages=%d, max_age_seconds=%s",
            max_messages,
            max_age_seconds,
        )

    def add_user_message(self, content: str) -> None:
        """
        Add a user message to memory.

        Args:
            content: User's utterance text.
        """
        message = ConversationMessage(
            role="user",
            content=content,
        )
        self._add_message(message)

    def add_assistant_message(self, content: str) -> None:
        """
        Add an assistant message to memory.

        Args:
            content: Assistant's response text.
        """
        message = ConversationMessage(
            role="assistant",
            content=content,
        )
        self._add_message(message)

    def _add_message(self, message: ConversationMessage) -> None:
        """
        Add a message to memory and enforce size constraints.

        Args:
            message: Message to add.
        """
        self._messages.append(message)

        logger.debug(
            "Added message to memory: role=%s, "
            "length=%d, total_messages=%d",
            message.role,
            len(message.content),
            len(self._messages),
        )

        # Enforce max messages
        if len(self._messages) > self._max_messages:
            removed = self._messages.pop(0)
            logger.debug(
                "Removed oldest message due to size limit: %s",
                removed.role,
            )

    def get_recent_history(
        self,
        num_messages: int = 10,
    ) -> list[ConversationMessage]:
        """
        Get the most recent messages from memory.

        Args:
            num_messages: Number of recent messages to retrieve.

        Returns:
            List of recent conversation messages.
        """
        # Filter out expired messages
        now = datetime.now()
        active_messages = []

        for msg in self._messages:
            if self._max_age_seconds is not None:
                age = (now - msg.timestamp).total_seconds()
                if age > self._max_age_seconds:
                    continue
            active_messages.append(msg)

        # Return the most recent messages
        return active_messages[-num_messages:] if active_messages else []

    def get_full_history(self) -> list[ConversationMessage]:
        """
        Get all stored conversation messages.

        Returns:
            Complete conversation history.
        """
        now = datetime.now()
        active_messages = []

        for msg in self._messages:
            if self._max_age_seconds is not None:
                age = (now - msg.timestamp).total_seconds()
                if age > self._max_age_seconds:
                    continue
            active_messages.append(msg)

        return active_messages

    def get_context_string(
        self,
        num_messages: int = 10,
    ) -> str:
        """
        Get conversation history as a formatted string for LLM context.

        Args:
            num_messages: Number of recent messages to include.

        Returns:
            Formatted conversation context string.
        """
        recent = self.get_recent_history(num_messages)

        if not recent:
            return ""

        lines = []
        for msg in recent:
            role_label = "User" if msg.role == "user" else "Assistant"
            lines.append(f"{role_label}: {msg.content}")

        return "\n".join(lines)

    def clear(self) -> None:
        """
        Clear all conversation memory.
        """
        cleared_count = len(self._messages)
        self._messages.clear()

        logger.info(
            "Conversation memory cleared. "
            "Removed %d messages.",
            cleared_count,
        )

    def get_size(self) -> dict:
        """
        Get memory statistics.

        Returns:
            Dictionary with size info.
        """
        now = datetime.now()
        active_count = 0

        for msg in self._messages:
            if self._max_age_seconds is not None:
                age = (now - msg.timestamp).total_seconds()
                if age > self._max_age_seconds:
                    continue
            active_count += 1

        return {
            "total_messages": len(self._messages),
            "active_messages": active_count,
            "max_messages": self._max_messages,
            "max_age_seconds": self._max_age_seconds,
        }
