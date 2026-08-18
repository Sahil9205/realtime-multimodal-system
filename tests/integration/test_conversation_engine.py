"""
Integration test for the conversation engine.

Tests the cumulative conversation pipeline:

    UserUtterance
        ↓
    ConversationEngine
        ↓
    IntentClassifier
        ↓
    IntentRouter
        ↓
    ConversationHandler
        ↓
    LLMService
        ↓
    LLMProvider
        ↓
    ConversationOutput
"""

from __future__ import annotations

import pytest

from app.ai.asr.schemas import UserUtterance
from app.conversation.engine import ConversationEngine
from app.conversation.schemas.conversation_output import ConversationOutput


@pytest.mark.anyio
async def test_conversation_engine_processes_user_utterance() -> None:
    """
    Verify that a completed UserUtterance can travel through
    the complete conversation engine and produce a response.
    """

    engine = ConversationEngine()

    utterance = UserUtterance(
        text="Hello Alisha",
        confidence=0.95,
    )

    response = await engine.process(utterance)

    assert isinstance(response, ConversationOutput)

    assert response.text.strip()

    print(f"\nUSER: {utterance.text}")
    print(f"ALISHA: {response.text}")