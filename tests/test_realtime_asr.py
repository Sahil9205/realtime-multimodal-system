"""
Tests for the Pipecat ASR processor.
"""

from __future__ import annotations

import asyncio

import pytest

from pipecat.frames.frames import (
    InputAudioRawFrame,
    TranscriptionFrame,
)

from app.ai.asr.base import BaseASR
from app.ai.asr.schemas import TranscriptionResult
from app.realtime.processors.asr import ASRProcessor


class FakeASR(BaseASR):
    """Deterministic fake ASR provider for processor tests."""

    def __init__(self) -> None:
        self.connected = False
        self.disconnected = False
        self.audio_chunks: list[bytes] = []

        self._transcript_queue: asyncio.Queue[
            TranscriptionResult
        ] = asyncio.Queue()

    async def connect(self) -> None:
        self.connected = True

        await self._transcript_queue.put(
            TranscriptionResult(
                transcript="hello alisha",
                is_final=True,
                speech_final=True,
                confidence=0.95,
            )
        )

    async def disconnect(self) -> None:
        self.disconnected = True

    async def send_audio(
        self,
        audio: bytes,
    ) -> None:
        self.audio_chunks.append(audio)

    async def receive_transcript(
        self,
    ) -> TranscriptionResult:
        return await self._transcript_queue.get()


@pytest.mark.anyio
async def test_asr_processor_sends_audio_to_provider() -> None:
    asr = FakeASR()
    processor = ASRProcessor(asr)

    await processor.start()

    frame = InputAudioRawFrame(
        audio=b"\x00\x01\x02\x03",
        sample_rate=16000,
        num_channels=1,
    )

    await processor.process_frame(
        frame,
        direction=None,
    )

    assert asr.connected is True
    assert asr.audio_chunks == [
        b"\x00\x01\x02\x03",
    ]

    await processor.stop()

    assert asr.disconnected is True


@pytest.mark.anyio
async def test_asr_processor_emits_transcription_frame() -> None:
    asr = FakeASR()
    processor = ASRProcessor(asr)

    emitted: list = []

    async def capture(frame, direction):
        emitted.append(frame)

    processor.push_frame = capture

    await processor.start()

    # Give the processor's receive task a chance to consume
    # the deterministic FakeASR transcript.
    for _ in range(100):
        if any(
            isinstance(frame, TranscriptionFrame)
            and frame.text == "hello alisha"
            and frame.finalized is True
            for frame in emitted
        ):
            break

        await asyncio.sleep(0.01)

    await processor.stop()

    assert any(
        isinstance(frame, TranscriptionFrame)
        and frame.text == "hello alisha"
        and frame.finalized is True
        for frame in emitted
    )