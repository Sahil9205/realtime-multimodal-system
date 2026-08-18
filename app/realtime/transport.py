"""
Small WebRTC transport configuration.
"""

from __future__ import annotations

from pipecat.transports.base_transport import TransportParams
from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport


def create_webrtc_connection() -> SmallWebRTCConnection:
    """
    Create a SmallWebRTC connection.
    """
    return SmallWebRTCConnection()


def create_webrtc_transport(
    connection: SmallWebRTCConnection,
) -> SmallWebRTCTransport:
    """
    Create a SmallWebRTC transport configured for
    bidirectional audio.
    """

    params = TransportParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
    )

    return SmallWebRTCTransport(
        webrtc_connection=connection,
        params=params,
    )