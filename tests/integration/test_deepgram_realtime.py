"""
Real Deepgram streaming ASR integration test.

Requires:
- DEEPGRAM_API_KEY
- microphone
- sounddevice
"""

from __future__ import annotations

import asyncio

from app.ai.asr.deepgram import DeepgramASR
from app.audio.microphone import Microphone
from app.core.config import settings


SAMPLE_RATE = settings.SAMPLE_RATE
CHANNELS = settings.CHANNELS
DURATION_SECONDS = 5


async def stream_microphone(asr: DeepgramASR) -> None:
    print()
    print("=" * 60)
    print("Speak now...")
    print("Say: Hello Alisha")
    print("=" * 60)

    microphone = Microphone()
    microphone.start()
    loop = asyncio.get_running_loop()

    try:
        deadline = loop.time() + DURATION_SECONDS

        while loop.time() < deadline:
            audio_chunk = await asyncio.to_thread(
                microphone.read,
            )

            if audio_chunk.data:
                await asr.send_audio(audio_chunk.data)
    finally:
        microphone.close()

    print("Recording and streaming finished.")


async def run_real_deepgram_test() -> None:
    asr = DeepgramASR()

    try:
        print("Connecting to Deepgram...")
        await asr.connect()
        print("Connected.")

        print("Streaming audio to Deepgram...")
        await stream_microphone(asr)
        print("Audio stream sent.")
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
