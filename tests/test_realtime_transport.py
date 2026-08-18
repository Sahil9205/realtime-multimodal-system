"""
Tests for Small WebRTC transport configuration.
"""

from app.realtime.transport import (
    create_webrtc_connection,
    create_webrtc_transport,
)


def test_create_webrtc_connection() -> None:
    connection = create_webrtc_connection()

    assert connection is not None


def test_create_webrtc_transport() -> None:
    connection = create_webrtc_connection()

    transport = create_webrtc_transport(connection)

    assert transport is not None