import asyncio

from app.ai.tts.schemas import TTSRequest
from app.ai.tts.service import TTSService
from app.audio.output.system import SystemAudioOutput


async def main() -> None:
    tts = TTSService()
    audio_output = SystemAudioOutput()


    response = await tts.synthesize(
        TTSRequest(
            text="Hello, I am Alisha. Your voice system is working and i love you."
        )
    )
    print("TTS generated:", len(response.audio), "bytes")
    print("Format:", response.content_type)

    await audio_output.play(response)

    print("Audio playback completed.")


if __name__ == "__main__":
    asyncio.run(main())