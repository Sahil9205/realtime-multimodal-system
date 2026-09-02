"""
WebSocket transport layer for the real-time voice app.

This module provides the application-facing WebSocket manager that can be
used by a FastAPI or Starlette server to connect a client to the voice
pipeline. It keeps the transport separate from the Pipecat media stack.
"""

from __future__ import annotations

import asyncio
import json
from uuid import uuid4
from typing import Any, Callable, Protocol

from pipecat.frames.frames import (
    InputAudioRawFrame,
    OutputAudioRawFrame,
    TranscriptionFrame,
)
from pipecat.processors.frame_processor import FrameDirection

from app.ai.asr.deepgram import DeepgramASR
from app.ai.asr.base import BaseASR
from app.conversation.engine import ConversationEngine
from app.core.config import settings
from app.core.logging import get_logger
from app.realtime.processors.asr import ASRProcessor
from app.realtime.processors.conversation import ConversationProcessor
from app.realtime.processors.tts import TTSProcessor
from app.realtime.frames.conversation import ConversationResponseFrame

logger = get_logger(__name__)


class WebSocketLike(Protocol):
    """Minimal websocket protocol used by the app manager."""

    async def accept(self) -> None: ...
    async def receive_text(self) -> str: ...
    async def receive(self) -> dict[str, Any]: ...
    async def send_text(self, message: str) -> None: ...
    async def send_bytes(self, data: bytes) -> None: ...
    async def close(self) -> None: ...


class RealtimeWebSocketManager:
    """Handles client messages and routes them to the runtime."""

    def __init__(
        self,
        asr_factory: Callable[[], BaseASR] = DeepgramASR,
        conversation_engine_factory: Callable[[], ConversationEngine]
        = ConversationEngine,
    ) -> None:
        self._connected = False
        self._asr_factory = asr_factory
        self._conversation_engine_factory = conversation_engine_factory

    @property
    def connected(self) -> bool:
        return self._connected

    async def handle_connection(self, websocket: WebSocketLike) -> None:
        """Accept a websocket and stream audio through the voice pipeline."""
        await websocket.accept()
        self._connected = True
        session_id = uuid4().hex[:8]
        logger.info("VOICE SESSION %s | started", session_id)

        asr_processor: ASRProcessor | None = None
        conversation_processor: ConversationProcessor | None = None
        response_task: asyncio.Task[None] | None = None
        send_lock = asyncio.Lock()

        async def send_json(payload: dict[str, Any]) -> None:
            async with send_lock:
                await websocket.send_text(json.dumps(payload))

        async def output_sink(frame, direction) -> None:
            if isinstance(frame, TranscriptionFrame):
                await send_json(
                    {
                        "type": "transcript",
                        "text": frame.text,
                        "final": frame.finalized,
                    }
                )
                return

            if isinstance(frame, ConversationResponseFrame):
                await send_json(
                    {
                        "type": "response",
                        "text": frame.text,
                    }
                )
                return

            if isinstance(frame, OutputAudioRawFrame):
                logger.info(
                    "VOICE SESSION %s | TTS complete; sending %d audio bytes",
                    session_id,
                    len(frame.audio),
                )
                await send_json(
                    {
                        "type": "audio",
                        "sample_rate": frame.sample_rate,
                        "channels": frame.num_channels,
                        "encoding": "audio/mpeg",
                    }
                )
                async with send_lock:
                    await websocket.send_bytes(frame.audio)

        async def start_pipeline() -> None:
            nonlocal asr_processor, conversation_processor

            if asr_processor is not None:
                return

            asr_processor = ASRProcessor(self._asr_factory())
            conversation_processor = ConversationProcessor(
                self._conversation_engine_factory()
            )
            tts_processor = TTSProcessor()

            async def conversation_output(frame, direction) -> None:
                if isinstance(frame, ConversationResponseFrame):
                    logger.info(
                        "VOICE SESSION %s | LLM response -> TTS: %r",
                        session_id,
                        frame.text,
                    )
                    await send_json({"type": "response", "text": frame.text})
                await tts_processor.process_frame(frame, direction)

            async def run_response(
                frame: TranscriptionFrame,
            ) -> None:
                """Generate one cancellable assistant response turn."""
                try:
                    logger.info(
                        "VOICE SESSION %s | transcript -> LLM: %r",
                        session_id,
                        frame.text,
                    )
                    await conversation_processor.process_frame(
                        frame,
                        FrameDirection.DOWNSTREAM,
                    )
                except asyncio.CancelledError:
                    logger.info("Assistant response cancelled by user interrupt.")
                    raise

            async def cancel_active_response() -> None:
                """Stop the active LLM/TTS turn without clearing memory."""
                nonlocal response_task

                if response_task is None or response_task.done():
                    return

                response_task.cancel()
                try:
                    await response_task
                except asyncio.CancelledError:
                    pass
                finally:
                    response_task = None

            async def asr_output(frame, direction) -> None:
                nonlocal response_task

                if isinstance(frame, TranscriptionFrame):
                    logger.info(
                        "VOICE SESSION %s | ASR final transcript: %r",
                        session_id,
                        frame.text,
                    )
                    await output_sink(frame, direction)
                    # A later user utterance supersedes any unfinished answer.
                    await cancel_active_response()
                    response_task = asyncio.create_task(run_response(frame))

            asr_processor.push_frame = asr_output
            conversation_processor.push_frame = conversation_output
            tts_processor.push_frame = output_sink

            await asr_processor.start()
            await send_json({"type": "ready"})
            logger.info("VOICE SESSION %s | audio pipeline ready", session_id)

        while True:
            try:
                message = await self._receive_message(websocket)
            except Exception:
                logger.warning("WebSocket receive failed; closing connection.")
                break

            if message is None:
                break

            if isinstance(message, bytes):
                await start_pipeline()
                await asr_processor.process_frame(
                    InputAudioRawFrame(
                        audio=message,
                        sample_rate=settings.SAMPLE_RATE,
                        num_channels=settings.CHANNELS,
                    ),
                    FrameDirection.DOWNSTREAM,
                )
                continue

            payload = message.strip()
            if not payload:
                continue

            try:
                command = json.loads(payload)
            except json.JSONDecodeError:
                command = {"type": "text", "text": payload}

            command_type = command.get("type")

            if command_type == "start":
                await start_pipeline()
                continue

            if command_type == "interrupt" or "interrupt" in payload.lower():
                logger.info("VOICE SESSION %s | user interruption", session_id)
                if response_task is not None and not response_task.done():
                    response_task.cancel()
                    try:
                        await response_task
                    except asyncio.CancelledError:
                        pass
                    finally:
                        response_task = None
                await send_json({"type": "interrupt", "status": "accepted"})
                continue

            if command_type == "stop":
                logger.info("VOICE SESSION %s | microphone stopped", session_id)
                continue

            # Keep the existing text smoke-test behavior until the frontend
            # starts sending binary PCM frames.
            if "hello" in payload.lower() or "hi" in payload.lower():
                await send_json(
                    {
                        "type": "text",
                        "text": "Hello! I am ready to help.",
                    }
                )
            else:
                await send_json({"type": "text", "text": "Message received."})

        self._connected = False
        if response_task is not None and not response_task.done():
            response_task.cancel()
            try:
                await response_task
            except asyncio.CancelledError:
                pass
        if asr_processor is not None:
            await asr_processor.stop()

        try:
            await websocket.close()
        except Exception:
            pass

        logger.info("VOICE SESSION %s | ended", session_id)

    async def _receive_message(
        self,
        websocket: WebSocketLike,
    ) -> str | bytes | None:
        """Read either binary PCM audio or a text control message."""

        if hasattr(websocket, "receive"):
            message = await websocket.receive()

            if message.get("type") == "websocket.disconnect":
                return None

            if message.get("bytes") is not None:
                return message["bytes"]

            return message.get("text")

        message = await websocket.receive_text()
        return message or None
