"""
Integration test for the complete real-time voice pipeline.

Pipeline:

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
    LLM
        ↓
    ConversationResponseFrame
        ↓
    TTSProcessor
        ↓
    OutputAudioRawFrame
"""

from __future__ import annotations

import asyncio

import pytest
import sounddevice as sd

from pipecat.frames.frames import (
    InputAudioRawFrame,
    OutputAudioRawFrame,
    StartFrame,
    TranscriptionFrame,
)
from pipecat.processors.frame_processor import FrameDirection

from app.ai.asr.deepgram import DeepgramASR
from app.realtime.processors.asr import ASRProcessor
from app.realtime.processors.conversation import ConversationProcessor
from app.realtime.processors.tts import TTSProcessor
from app.realtime.frames.conversation import ConversationResponseFrame


SAMPLE_RATE = 16000
CHANNELS = 1

RECORD_SECONDS = 6

CHUNK_SIZE = 2048

CHUNK_DURATION_SECONDS = (
    CHUNK_SIZE / (SAMPLE_RATE * 2 * CHANNELS)
)


@pytest.mark.anyio
async def test_realtime_asr_conversation_tts() -> None:
    """
    Test the cumulative voice pipeline:

        Microphone
            ↓
        ASR
            ↓
        Conversation
            ↓
        LLM
            ↓
        TTS
            ↓
        OutputAudioRawFrame
    """

    asr = DeepgramASR()

    asr_processor = ASRProcessor(asr)

    conversation_processor = ConversationProcessor()

    tts_processor = TTSProcessor()

    emitted_frames: list = []

    # --------------------------------------------------------------
    # Final sink
    # --------------------------------------------------------------

    async def capture(
        frame,
        direction: FrameDirection,
    ):
        emitted_frames.append(frame)

        return None

    # --------------------------------------------------------------
    # TTS → final sink
    # --------------------------------------------------------------

    tts_processor.push_frame = capture

    # --------------------------------------------------------------
    # Conversation → TTS
    # --------------------------------------------------------------

    async def forward_to_tts(
        frame,
        direction: FrameDirection,
    ):
        await tts_processor.process_frame(
            frame,
            direction,
        )

    conversation_processor.push_frame = forward_to_tts

    # --------------------------------------------------------------
    # ASR → Conversation
    # --------------------------------------------------------------

    async def forward_to_conversation(
        frame,
        direction: FrameDirection,
    ):
        await conversation_processor.process_frame(
            frame,
            direction,
        )

    asr_processor.push_frame = forward_to_conversation

    try:

        # ==========================================================
        # 1. Start processors
        # ==========================================================

        await asr_processor.start()

        # ==========================================================
        # 2. Pipecat lifecycle
        # ==========================================================

        start_frame = StartFrame(
            audio_in_sample_rate=SAMPLE_RATE,
            audio_out_sample_rate=24000,
        )

        await asr_processor.process_frame(
            start_frame,
            FrameDirection.DOWNSTREAM,
        )

        await conversation_processor.process_frame(
            start_frame,
            FrameDirection.DOWNSTREAM,
        )

        await tts_processor.process_frame(
            start_frame,
            FrameDirection.DOWNSTREAM,
        )

        # ==========================================================
        # 3. Record microphone
        # ==========================================================

        print()
        print("=" * 60)
        print(
            f"Speak for {RECORD_SECONDS} seconds."
        )
        print()
        print("Try saying:")
        print("  Hello Alisha.")
        print("  How are you?")
        print("  What can you do?")
        print("=" * 60)

        audio = sd.rec(
            int(
                RECORD_SECONDS * SAMPLE_RATE
            ),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
        )

        sd.wait()

        audio_bytes = audio.tobytes()

        print()
        print("Recording finished.")
        print(
            f"Captured {len(audio_bytes)} bytes."
        )

        # ==========================================================
        # 4. Stream audio through ASR
        # ==========================================================

        print()
        print(
            "Streaming audio through "
            "ASRProcessor..."
        )

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
                FrameDirection.DOWNSTREAM,
            )

            # Simulate real-time microphone timing.
            await asyncio.sleep(
                CHUNK_DURATION_SECONDS
            )

        print(
            "Finished streaming audio."
        )

        # ==========================================================
        # 5. Finalize Deepgram
        # ==========================================================

        print(
            "Finalizing Deepgram stream..."
        )

        await asr.finalize()

        # ==========================================================
        # 6. Wait for complete pipeline
        # ==========================================================

        print()
        print(
            "Waiting for "
            "ASR → Conversation → LLM → TTS..."
        )

        timeout = 20.0

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

            audio_frames = [
                frame
                for frame in emitted_frames
                if isinstance(
                    frame,
                    OutputAudioRawFrame,
                )
            ]

            if responses and audio_frames:
                break

            await asyncio.sleep(0.1)

        # ==========================================================
        # 7. Inspect results
        # ==========================================================

        responses = [
            frame
            for frame in emitted_frames
            if isinstance(
                frame,
                ConversationResponseFrame,
            )
        ]

        audio_frames = [
            frame
            for frame in emitted_frames
            if isinstance(
                frame,
                OutputAudioRawFrame,
            )
        ]

        transcription_frames = [
            frame
            for frame in emitted_frames
            if isinstance(
                frame,
                TranscriptionFrame,
            )
        ]

        print()
        print("=" * 60)

        print(
            f"TranscriptionFrames: "
            f"{len(transcription_frames)}"
        )

        print(
            f"ConversationResponseFrames: "
            f"{len(responses)}"
        )

        print(
            f"OutputAudioRawFrames: "
            f"{len(audio_frames)}"
        )

        print("=" * 60)

        for frame in transcription_frames:
            print(
                f"USER: {frame.text!r} "
                f"| finalized={frame.finalized}"
            )

        for frame in responses:
            print(
                f"ALISHA TEXT: {frame.text!r}"
            )

        for frame in audio_frames:
            print(
                f"AUDIO: {len(frame.audio)} bytes "
                f"| sample_rate={frame.sample_rate} "
                f"| channels={frame.num_channels}"
            )

        # ==========================================================
        # 8. Assertions
        # ==========================================================

        assert transcription_frames, (
            "No TranscriptionFrame reached "
            "the conversation pipeline."
        )

        assert responses, (
            "No ConversationResponseFrame "
            "was produced."
        )

        assert audio_frames, (
            "No OutputAudioRawFrame "
            "was produced by TTSProcessor."
        )

        for frame in audio_frames:
            assert frame.audio
            assert len(frame.audio) > 0

    finally:

        # ==========================================================
        # Cleanup
        # ==========================================================

        await asr.disconnect()