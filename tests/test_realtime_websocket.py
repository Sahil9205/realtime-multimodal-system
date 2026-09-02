import asyncio

import pytest

from app.ai.asr.base import BaseASR
from app.ai.asr.schemas import TranscriptionResult
from app.realtime.websocket import RealtimeWebSocketManager


class FakeWebSocket:
    def __init__(self):
        self.accepted = False
        self.sent = []
        self.messages = [
            '{"type": "text", "text": "Hello there"}',
            '{"type": "interrupt"}',
        ]

    async def accept(self):
        self.accepted = True

    async def receive_text(self):
        if not self.messages:
            await self.close()
            return ""
        return self.messages.pop(0)

    async def send_text(self, message: str):
        self.sent.append(message)

    async def close(self):
        self.closed = True


@pytest.mark.anyio
async def test_websocket_manager_handles_text_and_interrupt() -> None:
    websocket = FakeWebSocket()
    manager = RealtimeWebSocketManager()

    await manager.handle_connection(websocket)

    assert websocket.accepted is True
    assert any('hello' in msg.lower() for msg in websocket.sent)
    assert any('interrupt' in msg.lower() for msg in websocket.sent)


class BinaryFakeWebSocket:
    def __init__(self) -> None:
        self.accepted = False
        self.closed = False
        self.sent: list[str] = []
        self.audio: list[bytes] = []
        self.messages = [
            {"type": "websocket.receive", "bytes": b"pcm"},
            {"type": "websocket.disconnect"},
        ]

    async def accept(self) -> None:
        self.accepted = True

    async def receive(self) -> dict:
        return self.messages.pop(0)

    async def send_text(self, message: str) -> None:
        self.sent.append(message)

    async def send_bytes(self, data: bytes) -> None:
        self.audio.append(data)

    async def close(self) -> None:
        self.closed = True


class BinaryFakeASR(BaseASR):
    def __init__(self) -> None:
        self.audio: list[bytes] = []

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def send_audio(self, audio: bytes) -> None:
        self.audio.append(audio)

    async def receive_transcript(self) -> TranscriptionResult:
        return await asyncio.Future()


@pytest.mark.anyio
async def test_websocket_manager_forwards_binary_audio_to_asr() -> None:
    websocket = BinaryFakeWebSocket()
    asr = BinaryFakeASR()
    manager = RealtimeWebSocketManager(asr_factory=lambda: asr)

    await manager.handle_connection(websocket)

    assert websocket.accepted is True
    assert asr.audio == [b"pcm"]
    assert any('"type": "ready"' in message for message in websocket.sent)
    assert websocket.closed is True
