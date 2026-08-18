"""FastAPI application bootstrap."""

from fastapi import FastAPI, WebSocket

from app.api.routers import chat_router, conversation_router, health_router
from app.realtime.websocket import RealtimeWebSocketManager


def create_app() -> FastAPI:
    """Create and configure the application."""
    app = FastAPI(title="Voice Assistant API")
    websocket_manager = RealtimeWebSocketManager()

    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(conversation_router)

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await websocket_manager.handle_connection(websocket)

    return app
