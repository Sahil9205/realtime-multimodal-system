"""
WebSocket transport layer for the real-time voice app.

This module provides the application-facing WebSocket manager that can be
used by a FastAPI or Starlette server to connect a client to the voice
pipeline. It keeps the transport separate from the Pipecat media stack.
"""

from __future__ import annotations

from typing import Any, Protocol

from app.core.logging import get_logger

logger = get_logger(__name__)


class WebSocketLike(Protocol):
    """Minimal websocket protocol used by the app manager."""

    async def accept(self) -> None: ...
    async def receive_text(self) -> str: ...
    async def send_text(self, message: str) -> None: ...
    async def close(self) -> None: ...


class RealtimeWebSocketManager:
    """Handles client messages and routes them to the runtime."""

    def __init__(self) -> None:
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    async def handle_connection(self, websocket: WebSocketLike) -> None:
        """Accept a websocket and process text messages."""
        await websocket.accept()
        self._connected = True

        while True:
            try:
                message = await websocket.receive_text()
            except Exception:
                logger.warning("WebSocket receive failed; closing connection.")
                break

            if not message:
                break

            payload = message.strip()
            if not payload:
                continue

            lower = payload.lower()

            if "interrupt" in lower:
                await websocket.send_text('{"type": "interrupt", "status": "accepted"}')
                continue

            if "hello" in lower or "hi" in lower:
                await websocket.send_text('{"type": "text", "text": "Hello! I am ready to help."}')
                continue

            await websocket.send_text('{"type": "text", "text": "Message received."}')

        self._connected = False
        try:
            await websocket.close()
        except Exception:
            pass

        logger.info("WebSocket connection closed.")
