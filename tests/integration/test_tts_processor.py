"""
Integration test for the TTSProcessor.

Pipeline under test:

    ConversationResponseFrame
        ↓
    TTSProcessor
        ↓
    TTSService
        ↓
    DeepgramTTS
        ↓
    OutputAudioRawFrame
"""

from __future__ import annotations

import pytest

from pipecat.frames.frames import OutputAudioRawFrame
from pipecat.processors.frame_processor import FrameDirection

from app.realtime.frames.conversation import ConversationResponseFrame
from app.realtime.processors.tts import TTSProcessor


@pytest.mark.anyio
async def test_tts_processor_generates_audio() -> None:
    """
    Verify that TTSProcessor converts a conversation response
    into a Pipecat OutputAudioRawFrame.
    """

    processor = TTSProcessor()

    emitted: list = []

    async def capture(frame, direction) -> None:
        emitted.append(frame)

    processor.push_frame = capture

    response_frame = ConversationResponseFrame(
        text="Hello, I am Alisha.",
    )

    await processor.process_frame(
        response_frame,
        FrameDirection.DOWNSTREAM,
    )

    audio_frames = [
        frame
        for frame in emitted
        if isinstance(
            frame,
            OutputAudioRawFrame,
        )
    ]

    print(
        f"\nReceived {len(audio_frames)} "
        "OutputAudioRawFrame(s)"
    )

    for frame in audio_frames:
        print(
            f"AUDIO: {len(frame.audio)} bytes "
            f"| sample_rate={frame.sample_rate} "
            f"| channels={frame.num_channels}"
        )

    assert audio_frames, (
        "TTSProcessor did not emit an "
        "OutputAudioRawFrame."
    )

    assert all(
        frame.audio
        for frame in audio_frames
    )

    assert all(
        frame.sample_rate > 0
        for frame in audio_frames
    )

    assert all(
        frame.num_channels > 0
        for frame in audio_frames
    )