from app.ai.tts.schemas import TTSRequest, TTSResponse


def test_tts_request_creates_successfully() -> None:
    request = TTSRequest(
        text="Hello Assistant",
    )

    assert request.text == "Hello Assistant"
    assert request.language == "en"


def test_tts_response_creates_successfully() -> None:
    response = TTSResponse(
        audio=b"fake-audio",
    )

    assert response.audio == b"fake-audio"
    assert response.content_type == "audio/wav"