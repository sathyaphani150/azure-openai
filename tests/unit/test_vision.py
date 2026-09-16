import io

import pytest
from PIL import Image

from helpdesk.clients.fakes import FakeAIProvider
from helpdesk.config import Settings
from helpdesk.errors import ValidationError
from helpdesk.services.vision import VisionService


def _png() -> bytes:
    stream = io.BytesIO()
    Image.new("RGB", (32, 32), "white").save(stream, format="PNG")
    return stream.getvalue()


@pytest.mark.asyncio
async def test_valid_image_is_analyzed() -> None:
    service = VisionService(Settings(ai_provider="fake"), FakeAIProvider())
    result = await service.analyze("error.png", _png())
    assert result.media_type == "image/png"
    assert "passed validation" in result.analysis


def test_invalid_image_is_rejected() -> None:
    service = VisionService(Settings(ai_provider="fake"), FakeAIProvider())
    with pytest.raises(ValidationError):
        service.validate(b"not an image")
