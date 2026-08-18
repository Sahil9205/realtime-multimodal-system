"""
Integration test for Deepgram streaming ASR.
"""

from __future__ import annotations

import asyncio

from app.ai.asr.deepgram import DeepgramASR
from app.audio.microphone import Microphone
from app.core.logging import setup_logging


async def transcript_listener(asr: DeepgramASR) -> None:
    """
    Continuously consume transcripts from Deepgram.
    """

    try:
        while True:
            result = await asr.receive_transcript()

            if not result.transcript:
                continue

            status = (
                "FINAL"
                if result.speech_final
                else "INTERIM"
            )

            print(
                f"\n[{status}] {result.transcript}",
                flush=True,
            )

    except asyncio.CancelledError:
        # Expected when the test shuts down.
        raise


async def main() -> None:
    """
    Stream microphone audio to Deepgram.
    """

    setup_logging()

    microphone = Microphone()
    asr = DeepgramASR()
    
    microphone.start()

    listener_task: asyncio.Task | None = None

    try:
        print("\nStarting Deepgram test...")
        print("Speak into your microphone.")
        print("Press Ctrl+C to stop.\n")

        # ----------------------------------------------------------
        # Connect to Deepgram
        # ----------------------------------------------------------
        await asr.connect()

        # ----------------------------------------------------------
        # Start transcript listener in the background
        # ----------------------------------------------------------
        listener_task = asyncio.create_task(
            transcript_listener(asr)
        )

        # ----------------------------------------------------------
        # Continuously capture and send microphone audio
        # ----------------------------------------------------------
        while True:

            chunk = await asyncio.to_thread(
                microphone.read
            )

            print(
                f"Audio chunk received: "
                f"{len(chunk.data)} bytes",
                flush=True,
            )

            if not chunk.data:
                continue

            await asr.send_audio(
                chunk.data
            )

    except KeyboardInterrupt:
        print("\nStopping test...")

    except Exception as exc:
        print(
            f"\nTest failed: {exc}"
        )

    finally:
        # ----------------------------------------------------------
        # Stop microphone
        # ----------------------------------------------------------
        microphone.close()

        # ----------------------------------------------------------
        # Stop transcript listener
        # ----------------------------------------------------------
        if listener_task is not None:
            listener_task.cancel()

            try:
                await listener_task
            except asyncio.CancelledError:
                pass

        # ----------------------------------------------------------
        # Disconnect from Deepgram
        # ----------------------------------------------------------
        await asr.disconnect()


if __name__ == "__main__":
    asyncio.run(main())