"""
Tests for the conversation engine.
"""

import pytest

from app.ai.asr.schemas import UserUtterance
from app.conversation.engine import ConversationEngine

@pytest.mark.anyio
async def test_conversation_engine_processes_greeting() -> None:
    engine = ConversationEngine()

    utterance = UserUtterance(
        text="Hello Alisha",
        confidence=0.95,
    )

    response = await engine.process(utterance)

    assert response is not None
    assert "Hello" in response.text

@pytest.mark.anyio
async def test_conversation_engine_processes_information_request() -> None:
    engine = ConversationEngine()

    utterance = UserUtterance(
        text="What can you do?",
        confidence=0.90,
    )

    response = await engine.process(utterance)

    assert response is not None
    assert "What can you do?" in response.text

@pytest.mark.anyio
async def test_conversation_engine_accepts_missing_confidence() -> None:
    engine = ConversationEngine()

    utterance = UserUtterance(
        text="Hello",
        confidence=None,
    )

    response = await  engine.process(utterance)

    assert response is not None