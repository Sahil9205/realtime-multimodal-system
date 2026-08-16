"""
Deepgram streaming ASR provider.
"""

from __future__ import annotations

import asyncio

from deepgram import AsyncDeepgramClient
from deepgram.core.events import EventType
from deepgram.listen.v1.types import (ListenV1Results,ListenV1SpeechStarted)

from app.ai.asr.base import BaseASR
from app.ai.asr.schemas import TranscriptionResult
from app.core.config import settings
from app.core.exceptions import ASRError
from app.core.logging import get_logger


logger = get_logger(__name__)


class DeepgramASR(BaseASR):
    """
    Streaming speech-to-text provider using Deepgram.
    """

    def __init__(self) -> None:
        if not settings.DEEPGRAM_API_KEY:
            raise ASRError(
                "DEEPGRAM_API_KEY is not configured."
            )

        self._client = AsyncDeepgramClient(
            api_key=settings.DEEPGRAM_API_KEY,
        )

        self._connection = None
        self._connection_context = None
        self._listener_task: asyncio.Task | None = None

        self._queue: asyncio.Queue[
            TranscriptionResult
        ] = asyncio.Queue()

    async def connect(self) -> None:
        """
        Establish a streaming connection with Deepgram.
        """

        if self._connection is not None:
            return

        try:
            self._connection_context = (
                self._client.listen.v1.connect(
                    model="nova-3",
                    language="en-US",
                    encoding="linear16",
                    sample_rate=settings.SAMPLE_RATE,
                    channels=settings.CHANNELS,
                    interim_results=True,
                    smart_format=True,
                    punctuate=True,
                    endpointing=3000,
                    vad_events=True,
                )
            )

            self._connection = (
                await self._connection_context.__aenter__()
            )

            self._register_events()

            self._listener_task = asyncio.create_task(
                self._connection.start_listening()
            )

            logger.info(
                "Deepgram listener started."
            )

            logger.info(
                "Connected to Deepgram: "
                "model=nova-3 sample_rate=%s channels=%s",
                settings.SAMPLE_RATE,
                settings.CHANNELS,
            )

        except Exception as exc:
            logger.exception(
                "Failed to connect to Deepgram."
            )

            self._connection = None
            self._connection_context = None

            raise ASRError(
                "Could not connect to Deepgram."
            ) from exc

    async def disconnect(self) -> None:
        """
        Close the Deepgram streaming connection.
        """

        if self._connection_context is None:
            return

        try:
            if self._listener_task is not None:
                self._listener_task.cancel()

                try:
                    await self._listener_task
                except asyncio.CancelledError:
                    pass

            await self._connection_context.__aexit__(
                None,
                None,
                None,
            )

            logger.info(
                "Disconnected from Deepgram."
            )

        except Exception as exc:
            logger.exception(
                "Failed to disconnect from Deepgram."
            )

            raise ASRError(
                "Failed to disconnect from Deepgram."
            ) from exc

        finally:
            self._connection = None
            self._connection_context = None
            self._listener_task = None


    async def finalize(self) -> None:
        if self._connection is None:
            raise ASRError(
                "Deepgram connection is not established."
            )

        try:
            await self._connection.send_finalize()
            logger.debug("Sent Deepgram Finalize.")
        except Exception as exc:
            logger.exception("Failed to finalize Deepgram stream.")
            raise ASRError(
                "Failed to finalize Deepgram stream."
            ) from exc

    async def send_audio(
        self,
        audio: bytes,
    ) -> None:
        """
        Send a raw PCM audio chunk to Deepgram.
        """

        if self._connection is None:
            raise ASRError(
                "Deepgram connection is not established."
            )

        if not audio:
            logger.debug(
                "Ignoring empty audio chunk."
            )
            return

        try:
            await self._connection.send_media(audio)

        except Exception as exc:
            logger.exception(
                "Failed to send audio to Deepgram."
            )

            raise ASRError(
                "Failed to send audio to Deepgram."
            ) from exc

    async def receive_transcript(
        self,
    ) -> TranscriptionResult:
        """
        Wait for the next transcription result.
        """

        return await self._queue.get()

    def _register_events(self) -> None:
        """
        Register Deepgram WebSocket event handlers.
        """

        if self._connection is None:
            raise ASRError(
                "Deepgram connection is not available."
            )

        async def on_message(message) -> None:
            """
            Handle incoming Deepgram messages.
            """

            # ----------------------------------------------------------
            # Speech started
            # ----------------------------------------------------------
            logger.info(
                "DEEPGRAM EVENT: %s | %r",
                type(message).__name__,
                message,
            )

            if isinstance(message, ListenV1SpeechStarted):
                logger.debug(
                    "Speech started: timestamp=%s",
                    message.timestamp,
                )
                return


            # ----------------------------------------------------------
            # Transcription result
            # ----------------------------------------------------------


            if not isinstance(message,ListenV1Results,):


                logger.debug(
                    "Ignoring Deepgram event: %s",
                    type(message).__name__,
                )
                return

            if not message.channel:
                logger.debug(
                    "Deepgram result contains no channel."
                )
                return

            if not message.channel.alternatives:
                logger.debug(
                    "Deepgram result contains no alternatives."
                )
                return

            alternative = message.channel.alternatives[0]

            transcript = alternative.transcript.strip()

            # Deepgram can legitimately send empty Results while
            # speech is being detected.

            if not transcript:
                return

            result = TranscriptionResult(
                transcript=transcript,
                is_final=message.is_final,
                speech_final=message.speech_final,
                confidence=alternative.confidence,
            )

            await self._queue.put(result)

            logger.info(
                "Transcript: %r | final=%s | speech_final=%s",
                transcript,
                message.is_final,
                message.speech_final,
                alternative.confidence,
            )

        def on_open(message) -> None:
            logger.debug(
                "Deepgram WebSocket opened."
            )

        def on_close(message) -> None:
            logger.info(
                "Deepgram WebSocket closed."
            )

        def on_error(error) -> None:
            logger.error(
                "Deepgram WebSocket error: %s",
                error,
            )

        self._connection.on(
            EventType.OPEN,
            on_open,
        )

        self._connection.on(
            EventType.MESSAGE,
            on_message,
        )

        self._connection.on(
            EventType.CLOSE,
            on_close,
        )

        self._connection.on(
            EventType.ERROR,
            on_error,
        )