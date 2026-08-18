"""
Real Pipecat + Deepgram ASR processor integration test.

This test verifies the complete chain:

Microphone
    ↓
Pipecat InputAudioRawFrame
    ↓
ASRProcessor
    ↓
DeepgramASR
    ↓
Deepgram transcript
    ↓
UtteranceManager
    ↓
Pipecat TranscriptionFrame

Requirements:
    - DEEPGRAM_API_KEY configured
    - working microphone
    - sounddevice
    - internet connection

Run:
    python -m pytest tests/integration/test_realtime_deepgram_processor.py -v -s
"""

from __future__ import annotations

import asyncio

import pytest
import sounddevice as sd

from pipecat.frames.frames import (
    InputAudioRawFrame,
    StartFrame,
    TranscriptionFrame,
)

from app.ai.asr.deepgram import DeepgramASR
from app.core.config import settings
from app.realtime.processors.asr import ASRProcessor


SAMPLE_RATE = settings.SAMPLE_RATE
CHANNELS = settings.CHANNELS

# Record long enough to allow natural pauses.
RECORD_SECONDS = 10

# 100 ms of 16-bit mono PCM at 16 kHz.
CHUNK_DURATION_SECONDS = 0.1

CHUNK_SIZE = int(
    SAMPLE_RATE
    * CHANNELS
    * 2
    * CHUNK_DURATION_SECONDS
)


@pytest.mark.anyio
async def test_realtime_deepgram_processor() -> None:
    """
    Test the complete real-time ASR pipeline using:

        Microphone
            ↓
        ASRProcessor
            ↓
        DeepgramASR
            ↓
        UtteranceManager
            ↓
        TranscriptionFrame
    """

    asr = DeepgramASR()
    processor = ASRProcessor(asr)

    emitted: list = []

    async def capture(frame, direction):
        emitted.append(frame)

    # Capture frames emitted by ASRProcessor.
    processor.push_frame = capture

    try:
        # --------------------------------------------------------------
        # 1. Start ASR processor
        # --------------------------------------------------------------

        await processor.start()

        # --------------------------------------------------------------
        # 2. Start Pipecat lifecycle
        # --------------------------------------------------------------

        await processor.process_frame(
            StartFrame(
                audio_in_sample_rate=SAMPLE_RATE,
                audio_out_sample_rate=24000,
            ),
            None,
        )

        # --------------------------------------------------------------
        # 3. Record microphone audio
        # --------------------------------------------------------------

        print()
        print("=" * 60)
        print(f"Speak naturally for {RECORD_SECONDS} seconds.")
        print()
        print("Try saying:")
        print("  Hello Alisha.")
        print("  How are you?")
        print("  What can you do?")
        print()
        print("You can pause while speaking.")
        print("Deepgram endpointing is configured for 3 seconds.")
        print("=" * 60)

        audio = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
        )

        sd.wait()

        audio_bytes = audio.tobytes()

        print()
        print("Recording finished.")
        print(f"Captured {len(audio_bytes)} bytes.")

        # --------------------------------------------------------------
        # 4. Stream audio to ASRProcessor in small chunks
        # --------------------------------------------------------------

        print()
        print("Streaming audio to Deepgram...")

        for start in range(
            0,
            len(audio_bytes),
            CHUNK_SIZE,
        ):
            chunk = audio_bytes[
                start : start + CHUNK_SIZE
            ]

            if not chunk:
                continue

            await processor.process_frame(
                InputAudioRawFrame(
                    audio=chunk,
                    sample_rate=SAMPLE_RATE,
                    num_channels=CHANNELS,
                ),
                None,
            )

            # Simulate real-time microphone streaming.
            await asyncio.sleep(
                CHUNK_DURATION_SECONDS
            )

        print("Finished streaming audio.")

        # --------------------------------------------------------------
        # 5. Finalize the Deepgram stream
        # --------------------------------------------------------------

        print("Finalizing Deepgram stream...")

        await asr.finalize()

        # --------------------------------------------------------------
        # 6. Wait for transcription frames
        # --------------------------------------------------------------

        print("Waiting for transcription...")

        timeout_seconds = 12.0
        deadline = (
            asyncio.get_running_loop().time()
            + timeout_seconds
        )

        while (
            asyncio.get_running_loop().time()
            < deadline
        ):
            transcription_frames = [
                frame
                for frame in emitted
                if isinstance(
                    frame,
                    TranscriptionFrame,
                )
            ]

            if transcription_frames:
                break

            await asyncio.sleep(0.1)

        # --------------------------------------------------------------
        # 7. Inspect emitted frames
        # --------------------------------------------------------------

        transcription_frames = [
            frame
            for frame in emitted
            if isinstance(
                frame,
                TranscriptionFrame,
            )
        ]

        print()
        print(
            f"Received {len(transcription_frames)} "
            "TranscriptionFrame(s)"
        )

        for frame in transcription_frames:
            print(
                f"TRANSCRIPT: {frame.text!r} "
                f"| finalized={frame.finalized}"
            )

        # --------------------------------------------------------------
        # 8. Assertions
        # --------------------------------------------------------------

        assert transcription_frames, (
            "No TranscriptionFrame was emitted. "
            "Deepgram did not produce a transcript through "
            "ASRProcessor."
        )

        assert any(
            frame.text.strip()
            for frame in transcription_frames
        ), (
            "TranscriptionFrame(s) were emitted, "
            "but all transcripts were empty."
        )

    finally:
        # --------------------------------------------------------------
        # 9. Always clean up
        # --------------------------------------------------------------

        await processor.stop()