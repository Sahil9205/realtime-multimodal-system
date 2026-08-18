"""
End-to-end real-time voice pipeline integration test.

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
    LLMService
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
from app.core.config import settings


SAMPLE_RATE = settings.SAMPLE_RATE
CHANNELS = settings.CHANNELS

RECORD_SECONDS = 6

CHUNK_SIZE = 2048

CHUNK_DURATION_SECONDS = (
    CHUNK_SIZE / (SAMPLE_RATE * CHANNELS * 2)
)


@pytest.mark.anyio
async def test_realtime_voice_pipeline() -> None:
    """
    Test the complete real-time voice pipeline.

    Microphone
        ↓
    ASR
        ↓
    Conversation
        ↓
    TTS
        ↓
    Output audio
    """

    asr = DeepgramASR()

    asr_processor = ASRProcessor(asr)

    conversation_processor = ConversationProcessor()

    tts_processor = TTSProcessor()

    emitted_frames: list = []

    # --------------------------------------------------------------
    # Final output collector
    # --------------------------------------------------------------

    async def capture(
        frame,
        direction: FrameDirection,
    ) -> None:

        emitted_frames.append(frame)

        print(
            f"FRAME: {type(frame).__name__}"
        )

    # --------------------------------------------------------------
    # TTS → final output
    # --------------------------------------------------------------

    tts_processor.push_frame = capture

    # --------------------------------------------------------------
    # Conversation → TTS
    # --------------------------------------------------------------

    async def forward_to_tts(
        frame,
        direction: FrameDirection,
    ) -> None:

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
    ) -> None:

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
        print(
            f"Captured {len(audio_bytes)} bytes."
        )

        # ==========================================================
        # 4. Stream microphone audio
        # ==========================================================

        print()
        print(
            "Streaming audio through ASR..."
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
        # 5. Finalize ASR
        # ==========================================================

        print(
            "Finalizing Deepgram..."
        )

        await asr.finalize()

        # ==========================================================
        # 6. Wait for complete pipeline
        # ==========================================================

        print()
        print(
            "Waiting for:"
        )
        print(
            "ASR → Conversation → LLM → TTS"
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

            audio_frames = [
                frame
                for frame in emitted_frames
                if isinstance(
                    frame,
                    OutputAudioRawFrame,
                )
            ]

            if audio_frames:
                break

            await asyncio.sleep(0.1)

        # ==========================================================
        # 7. Collect frames
        # ==========================================================

        transcription_frames = [
            frame
            for frame in emitted_frames
            if isinstance(
                frame,
                TranscriptionFrame,
            )
        ]

        response_frames = [
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

        # ==========================================================
        # 8. Print results
        # ==========================================================

        print()
        print("=" * 60)

        print(
            f"TranscriptionFrame(s): "
            f"{len(transcription_frames)}"
        )

        for frame in transcription_frames:
            print(
                f"TRANSCRIPT: {frame.text!r}"
            )

        print()

        print(
            f"ConversationResponseFrame(s): "
            f"{len(response_frames)}"
        )

        for frame in response_frames:
            print(
                f"ALISHA: {frame.text!r}"
            )

        print()

        print(
            f"OutputAudioRawFrame(s): "
            f"{len(audio_frames)}"
        )

        for frame in audio_frames:
            print(
                f"AUDIO: {len(frame.audio)} bytes "
                f"| sample_rate={frame.sample_rate} "
                f"| channels={frame.num_channels}"
            )

        print("=" * 60)

        # ==========================================================
        # 9. Assertions
        # ==========================================================

        assert transcription_frames, (
            "ASR produced no TranscriptionFrame."
        )

        assert response_frames, (
            "Conversation produced no "
            "ConversationResponseFrame."
        )

        assert audio_frames, (
            "TTS produced no OutputAudioRawFrame."
        )

        assert all(
            frame.audio
            for frame in audio_frames
        ), (
            "At least one OutputAudioRawFrame "
            "contains empty audio."
        )

    finally:

        # ==========================================================
        # 10. Cleanup
        # ==========================================================

        try:
            await asr.disconnect()
        except Exception:
            pass