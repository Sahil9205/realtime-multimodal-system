"""
WebRTC signaling service.
"""

from __future__ import annotations

from dataclasses import dataclass

from pipecat.transports.smallwebrtc.connection import (
    SmallWebRTCConnection,
)


@dataclass(frozen=True)
class WebRTCOffer:
    """
    SDP offer received from the client.
    """

    sdp: str
    type: str = "offer"


@dataclass(frozen=True)
class WebRTCAnswer:
    """
    SDP answer returned to the client.
    """

    sdp: str
    type: str


class WebRTCSignaling:
    """
    Handles WebRTC SDP offer/answer negotiation.

    This layer is responsible only for signaling.
    Actual media transport is handled by Pipecat's
    SmallWebRTCTransport.
    """

    async def create_answer(
        self,
        offer: WebRTCOffer,
        connection: SmallWebRTCConnection | None = None,
    ) -> tuple[WebRTCAnswer, SmallWebRTCConnection]:
        """
        Create an SDP answer for a client offer.

        Returns both the answer and the connection because
        the connection must remain alive for the subsequent
        WebRTC media session.
        """

        if not offer.sdp.strip():
            raise ValueError("SDP offer cannot be empty.")

        if offer.type != "offer":
            raise ValueError(
                f"Unsupported SDP type: {offer.type}"
            )

        connection = (
            connection
            if connection is not None
            else SmallWebRTCConnection()
        )

        await connection.initialize(
            offer.sdp,
            offer.type,
        )

        answer = await connection.get_answer()

        return (
            WebRTCAnswer(
                sdp=answer.sdp,
                type=answer.type,
            ),
            connection,
        )