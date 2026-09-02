"""Minimal FastAPI server for the voice assistant."""

from __future__ import annotations

from fastapi import FastAPI, Request, WebSocket

from app.core.logging import get_logger, setup_logging
from app.realtime.websocket import RealtimeWebSocketManager


# Configure logging before handling any HTTP or WebSocket traffic. Without this
# call, the application loggers inherit Python's unconfigured root logger and
# INFO/DEBUG records are silently discarded.
setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="Voice Assistant API")
websocket_manager = RealtimeWebSocketManager()


@app.middleware("http")
async def log_http_request(request: Request, call_next):
    """Log each API request and its response status."""
    logger.info("HTTP request started: %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info(
        "HTTP request completed: %s %s -> %s",
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


@app.get("/health")
async def health_check() -> dict[str, str]:
    logger.debug("Health check requested.")
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    logger.info("WebSocket connection requested: %s", websocket.client)
    await websocket_manager.handle_connection(websocket)
