"""
Cumulative real-time ASR → Conversation → LLM integration test.
"""

from __future__ import annotations

import asyncio

import pytest

from pipecat.frames.frames import (
    InputAudioRawFrame,
    StartFrame,
)

from app.ai.asr.deepgram import DeepgramASR
from app.realtime.frames.conversation import ConversationResponseFrame
from app.realtime.processors.asr import ASRProcessor
from app.realtime.processors.conversation import ConversationProcessor


SAMPLE_RATE = 16000
CHANNELS = 1

RECORD_SECONDS = 6

CHUNK_SIZE = 2048

CHUNK_DURATION_SECONDS = (
    CHUNK_SIZE / (SAMPLE_RATE * 2 * CHANNELS)
)


@pytest.mark.anyio
async def test_realtime_asr_to_conversation() -> None:
    """
    Test the cumulative real-time pipeline:

        Microphone
            ↓
        DeepgramASR
            ↓
        ASRProcessor
            ↓
        TranscriptionFrame
            ↓
        ConversationProcessor
            ↓
        ConversationEngine
            ↓
        LLMService
            ↓
        HuggingFaceLLM
            ↓
        ConversationResponseFrame
    """

    import sounddevice as sd

    asr = DeepgramASR()

    asr_processor = ASRProcessor(asr)

    conversation_processor = ConversationProcessor()

    emitted_frames: list = []

    async def capture(frame, direction):
        emitted_frames.append(frame)

        # ConversationProcessor is the final processor
        # in this test pipeline.
        #
        # We don't need to push further downstream.
        return None

    conversation_processor.push_frame = capture

    async def forward_to_conversation(frame, direction):
        await conversation_processor.process_frame(
            frame,
            direction,
        )

    asr_processor.push_frame = forward_to_conversation

    try:
        # ----------------------------------------------------------
        # 1. Start ASR
        # ----------------------------------------------------------

        await asr_processor.start()

        # ----------------------------------------------------------
        # 2. Pipecat lifecycle
        # ----------------------------------------------------------

        await asr_processor.process_frame(
            StartFrame(
                audio_in_sample_rate=SAMPLE_RATE,
                audio_out_sample_rate=24000,
            ),
            None,
        )

        # ----------------------------------------------------------
        # 3. Record microphone
        # ----------------------------------------------------------

        print()
        print("=" * 60)
        print(f"Speak for {RECORD_SECONDS} seconds.")
        print()
        print("Try saying:")
        print("  Hello Alisha.")
        print("  How are you?")
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

        # ----------------------------------------------------------
        # 4. Stream audio through ASRProcessor
        # ----------------------------------------------------------

        print()
        print("Streaming audio through ASRProcessor...")

        for start in range(
            0,
            len(audio_bytes),
            CHUNK_SIZE,
        ):
            chunk = audio_bytes[
                start:start + CHUNK_SIZE
            ]

            if not chunk:
                continue

            await asr_processor.process_frame(
                InputAudioRawFrame(
                    audio=chunk,
                    sample_rate=SAMPLE_RATE,
                    num_channels=CHANNELS,
                ),
                None,
            )

            await asyncio.sleep(
                CHUNK_DURATION_SECONDS
            )

        print("Finished streaming audio.")

        # ----------------------------------------------------------
        # 5. Finalize Deepgram
        # ----------------------------------------------------------

        print("Finalizing Deepgram stream...")

        await asr.finalize()

        # ----------------------------------------------------------
        # 6. Wait for complete pipeline
        # ----------------------------------------------------------

        print(
            "Waiting for ASR → Conversation → LLM..."
        )

        timeout = 15.0

        deadline = (
            asyncio.get_running_loop().time()
            + timeout
        )

        while (
            asyncio.get_running_loop().time()
            < deadline
        ):
            responses = [
                frame
                for frame in emitted_frames
                if isinstance(
                    frame,
                    ConversationResponseFrame,
                )
            ]

            if responses:
                break

            await asyncio.sleep(0.1)

        # ----------------------------------------------------------
        # 7. Inspect final responses
        # ----------------------------------------------------------

        responses = [
            frame
            for frame in emitted_frames
            if isinstance(
                frame,
                ConversationResponseFrame,
            )
        ]

        print()
        print(
            f"Received {len(responses)} "
            "ConversationResponseFrame(s)"
        )

        for response in responses:
            print(
                f"ALISHA: {response.text!r}"
            )

        # ----------------------------------------------------------
        # 8. Assertions
        # ----------------------------------------------------------

        assert responses, (
            "No ConversationResponseFrame was produced "
            "by the cumulative ASR → Conversation → LLM pipeline."
        )

        assert any(
            response.text.strip()
            for response in responses
        )

    finally:
        await asr_processor.stop()