"""API router registrations."""

from app.api.routers.chat import router as chat_router
from app.api.routers.conversations import router as conversation_router
from app.api.routers.health import router as health_router

__all__ = [
    "chat_router",
    "conversation_router",
    "health_router",
]
