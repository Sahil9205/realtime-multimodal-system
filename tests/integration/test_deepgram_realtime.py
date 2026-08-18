"""
Real Deepgram streaming ASR integration test.

Requires:
- DEEPGRAM_API_KEY
- microphone
- sounddevice
"""

from __future__ import annotations

import asyncio

import sounddevice as sd

from app.ai.asr.deepgram import DeepgramASR
from app.core.config import settings


SAMPLE_RATE = settings.SAMPLE_RATE
CHANNELS = settings.CHANNELS
DURATION_SECONDS = 5


def record_audio() -> bytes:
    print()
    print("=" * 60)
    print("Speak now...")
    print("Say: Hello Alisha")
    print("=" * 60)

    audio = sd.rec(
        int(DURATION_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
    )

    sd.wait()

    print("Recording finished.")

    return audio.tobytes()


async def run_real_deepgram_test() -> None:
    asr = DeepgramASR()

    try:
        print("Connecting to Deepgram...")
        await asr.connect()
        print("Connected.")

        audio = await asyncio.to_thread(record_audio)

        print("Sending audio to Deepgram...")
        await asr.send_audio(audio)
        print("Audio sent.")
        await asr.finalize()

        print("Waiting for transcript...")

        while True:
            result = await asyncio.wait_for(
                asr.receive_transcript(),
                timeout=10.0,
            )

            print(
                f"TRANSCRIPT: {result.transcript!r} "
                f"| final={result.is_final} "
                f"| speech_final={result.speech_final} "
                f"| confidence={result.confidence}"
            )

            if result.is_final:
                break

    finally:
        await asr.disconnect()
        print("Disconnected from Deepgram.")


def test_real_deepgram_streaming() -> None:
    asyncio.run(run_real_deepgram_test())
