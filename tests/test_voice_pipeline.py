"""
Tests for the voice pipeline.
"""

from __future__ import annotations

import pytest

from app.ai.asr.schemas import TranscriptionResult
from app.conversation.schemas.conversation_output import ConversationOutput
from app.voice.pipeline import VoicePipeline


pytestmark = pytest.mark.anyio


class FakeASR:
    """Fake ASR provider for unit testing."""

    def __init__(self) -> None:
        self.connected = False
        self.disconnected = False

        self._results = [
            TranscriptionResult(
                transcript="Hello Alisha",
                is_final=True,
                speech_final=True,
                confidence=0.95,
            )
        ]

    async def connect(self) -> None:
        self.connected = True

    async def disconnect(self) -> None:
        self.disconnected = True

    async def send_audio(self, audio: bytes) -> None:
        pass

    async def receive_transcript(self) -> TranscriptionResult:
        return self._results.pop(0)


class FakeConversationEngine:
    """Fake conversation engine for unit testing."""

    def __init__(self) -> None:
        self.received_utterances = []

    def process(self, utterance):
        self.received_utterances.append(utterance)

        return ConversationOutput(
            text=f"Fake response: {utterance.text}",
        )


async def test_pipeline_starts_asr() -> None:
    asr = FakeASR()

    pipeline = VoicePipeline(asr)

    await pipeline.start()

    assert asr.connected is True


async def test_pipeline_converts_transcription_to_conversation_output() -> None:
    asr = FakeASR()
    conversation_engine = FakeConversationEngine()

    pipeline = VoicePipeline(
        asr=asr,
        conversation_engine=conversation_engine,
    )

    await pipeline.start()

    output = await pipeline.process_next()

    assert output is not None
    assert output.text == "Fake response: Hello Alisha"


async def test_pipeline_passes_utterance_to_conversation_engine() -> None:
    asr = FakeASR()
    conversation_engine = FakeConversationEngine()

    pipeline = VoicePipeline(
        asr=asr,
        conversation_engine=conversation_engine,
    )

    await pipeline.start()

    await pipeline.process_next()

    assert len(conversation_engine.received_utterances) == 1

    utterance = conversation_engine.received_utterances[0]

    assert utterance.text == "Hello Alisha"
    assert utterance.confidence == 0.95


async def test_pipeline_stops_asr() -> None:
    asr = FakeASR()

    pipeline = VoicePipeline(asr)

    await pipeline.start()
    await pipeline.stop()

    assert asr.disconnected is True