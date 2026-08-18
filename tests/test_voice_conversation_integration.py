"""
End-to-end integration tests for the voice-to-conversation flow.
"""

from __future__ import annotations

import pytest

from app.ai.asr.schemas import TranscriptionResult
from app.conversation.engine import ConversationEngine
from app.voice.pipeline import VoicePipeline


pytestmark = pytest.mark.anyio


class FakeASR:
    """
    Fake ASR provider used to test the complete voice pipeline.
    """

    def __init__(
        self,
        transcript: str,
    ) -> None:
        self.connected = False
        self.disconnected = False

        self._result = TranscriptionResult(
            transcript=transcript,
            is_final=True,
            speech_final=True,
            confidence=0.95,
        )

    async def connect(self) -> None:
        self.connected = True

    async def disconnect(self) -> None:
        self.disconnected = True

    async def send_audio(self, audio: bytes) -> None:
        pass

    async def receive_transcript(
        self,
    ) -> TranscriptionResult:
        return self._result


async def test_voice_to_conversation_greeting() -> None:
    """
    Verify that a spoken greeting travels through the
    voice pipeline and reaches the conversation handler.
    """

    asr = FakeASR("Hello Alisha")

    conversation_engine = ConversationEngine()

    pipeline = VoicePipeline(
        asr=asr,
        utterance_manager=None,
        conversation_engine=conversation_engine,
    )

    await pipeline.start()

    response = await pipeline.process_next()

    assert response is not None
    assert "Hello" in response.text

    await pipeline.stop()


async def test_voice_to_conversation_information_request() -> None:
    """
    Verify that an information request travels through the
    voice pipeline and reaches the information handler.
    """

    asr = FakeASR("What can you do?")

    conversation_engine = ConversationEngine()

    pipeline = VoicePipeline(
        asr=asr,
        utterance_manager=None,
        conversation_engine=conversation_engine,
    )

    await pipeline.start()

    response = await pipeline.process_next()

    assert response is not None
    assert "What can you do?" in response.text

    await pipeline.stop()


async def test_voice_pipeline_stops_asr_after_conversation() -> None:
    """
    Verify that the ASR connection can be stopped after
    conversation processing is complete.
    """

    asr = FakeASR("Hello")

    conversation_engine = ConversationEngine()

    pipeline = VoicePipeline(
        asr=asr,
        utterance_manager=None,
        conversation_engine=conversation_engine,
    )

    await pipeline.start()

    response = await pipeline.process_next()

    assert response is not None

    await pipeline.stop()

    assert asr.connected is True
    assert asr.disconnected is True