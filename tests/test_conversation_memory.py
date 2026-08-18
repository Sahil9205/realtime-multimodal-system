"""
Tests for conversation memory.
"""

import pytest
from datetime import datetime, timedelta

from app.conversation.memory import ConversationMemory, ConversationMessage


def test_conversation_memory_add_messages() -> None:
    """Test adding messages to memory."""
    memory = ConversationMemory()

    memory.add_user_message("Hello, how are you?")
    memory.add_assistant_message("I'm doing great, thank you for asking!")
    
    history = memory.get_full_history()
    
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "Hello, how are you?"
    assert history[1].role == "assistant"
    assert history[1].content == "I'm doing great, thank you for asking!"


def test_conversation_memory_max_messages() -> None:
    """Test memory respects max message limit."""
    memory = ConversationMemory(max_messages=5)
    
    # Add 10 messages
    for i in range(10):
        if i % 2 == 0:
            memory.add_user_message(f"User message {i}")
        else:
            memory.add_assistant_message(f"Assistant message {i}")
    
    history = memory.get_full_history()
    
    # Should only have 5 most recent messages
    assert len(history) == 5
    assert "User message 8" in history[-2].content
    assert "Assistant message 9" in history[-1].content


def test_conversation_memory_recent_history() -> None:
    """Test retrieving recent messages."""
    memory = ConversationMemory()
    
    for i in range(10):
        if i % 2 == 0:
            memory.add_user_message(f"User {i}")
        else:
            memory.add_assistant_message(f"Assistant {i}")
    
    recent = memory.get_recent_history(num_messages=3)
    
    assert len(recent) == 3
    # Last 3 messages should be: Assistant 7, User 8, Assistant 9
    assert "Assistant 7" in recent[0].content
    assert "User 8" in recent[1].content
    assert "Assistant 9" in recent[2].content


def test_conversation_memory_context_string() -> None:
    """Test generating context string for LLM."""
    memory = ConversationMemory()
    
    memory.add_user_message("What is Python?")
    memory.add_assistant_message("Python is a programming language.")
    memory.add_user_message("How do I install it?")
    
    context = memory.get_context_string()
    
    assert "User: What is Python?" in context
    assert "Assistant: Python is a programming language." in context
    assert "User: How do I install it?" in context


def test_conversation_memory_clear() -> None:
    """Test clearing memory."""
    memory = ConversationMemory()
    
    memory.add_user_message("Test message 1")
    memory.add_assistant_message("Test response 1")
    
    assert len(memory.get_full_history()) == 2
    
    memory.clear()
    
    assert len(memory.get_full_history()) == 0


def test_conversation_memory_size_info() -> None:
    """Test getting memory size information."""
    memory = ConversationMemory(max_messages=10)
    
    memory.add_user_message("Message 1")
    memory.add_assistant_message("Response 1")
    
    size = memory.get_size()
    
    assert size["total_messages"] == 2
    assert size["active_messages"] == 2
    assert size["max_messages"] == 10


def test_conversation_memory_empty_context() -> None:
    """Test context string with empty memory."""
    memory = ConversationMemory()
    
    context = memory.get_context_string()
    
    assert context == ""


def test_conversation_memory_message_model() -> None:
    """Test ConversationMessage pydantic model."""
    msg = ConversationMessage(
        role="user",
        content="Test message"
    )
    
    assert msg.role == "user"
    assert msg.content == "Test message"
    assert isinstance(msg.timestamp, datetime)
