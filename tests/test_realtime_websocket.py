import pytest

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
