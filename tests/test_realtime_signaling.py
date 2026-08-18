"""
Tests for WebRTC signaling.
"""

import pytest

from app.realtime.signaling import (
    WebRTCAnswer,
    WebRTCOffer,
    WebRTCSignaling,
)


def test_web_rtc_offer_defaults_to_offer() -> None:
    offer = WebRTCOffer(
        sdp="test-sdp",
    )

    assert offer.sdp == "test-sdp"
    assert offer.type == "offer"


def test_web_rtc_answer_schema() -> None:
    answer = WebRTCAnswer(
        sdp="test-answer-sdp",
        type="answer",
    )

    assert answer.sdp == "test-answer-sdp"
    assert answer.type == "answer"


@pytest.mark.anyio
async def test_signaling_rejects_empty_sdp() -> None:
    signaling = WebRTCSignaling()

    offer = WebRTCOffer(
        sdp="",
    )

    with pytest.raises(ValueError, match="SDP offer cannot be empty"):
        await signaling.create_answer(offer)


@pytest.mark.anyio
async def test_signaling_rejects_invalid_sdp_type() -> None:
    signaling = WebRTCSignaling()

    offer = WebRTCOffer(
        sdp="test-sdp",
        type="answer",
    )

    with pytest.raises(ValueError, match="Unsupported SDP type"):
        await signaling.create_answer(offer)