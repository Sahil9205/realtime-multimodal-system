"""Minimal FastAPI server for the voice assistant."""

from __future__ import annotations

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.realtime.websocket import RealtimeWebSocketManager

app = FastAPI(title="Voice Assistant API")
websocket_manager = RealtimeWebSocketManager()


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket_manager.handle_connection(websocket)
