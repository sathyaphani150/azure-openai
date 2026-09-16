from __future__ import annotations

import base64
import io
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

from helpdesk.clients.protocols import AIProvider
from helpdesk.config import Settings
from helpdesk.errors import ValidationError
from helpdesk.observability.usage import elapsed_timer, log_usage
from helpdesk.prompts.vision import VISION_PROMPT
from helpdesk.schemas import VisionResponse

ALLOWED_FORMATS = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}


class VisionService:
    """Validate screenshots and submit safe multimodal analysis requests."""

    def __init__(self, settings: Settings, provider: AIProvider):
        self.settings = settings
        self.provider = provider

    def validate(self, content: bytes) -> str:
        """Validate image bytes, type, size, and decoded pixel dimensions."""
        if not content:
            raise ValidationError("The uploaded image is empty.")
        if len(content) > self.settings.max_image_bytes:
            raise ValidationError(
                f"The image exceeds the {self.settings.max_image_bytes // (1024 * 1024)} MB limit."
            )
        try:
            with Image.open(io.BytesIO(content)) as image:
                image.verify()
            with Image.open(io.BytesIO(content)) as image:
                media_type = ALLOWED_FORMATS.get(image.format or "")
                if not media_type:
                    raise ValidationError("Only PNG, JPEG, and WebP screenshots are supported.")
                if image.width * image.height > self.settings.max_image_pixels:
                    raise ValidationError("The screenshot dimensions are too large.")
                return media_type
        except ValidationError:
            raise
        except (UnidentifiedImageError, OSError) as exc:
            raise ValidationError("The uploaded file is not a valid supported image.") from exc

    async def analyze(
        self, filename: str, content: bytes, request_id: str | None = None
    ) -> VisionResponse:
        """Analyze a validated screenshot without persisting its contents."""
        request_id = request_id or str(uuid4())
        media_type = self.validate(content)
        data = base64.b64encode(content).decode("ascii")
        with elapsed_timer() as elapsed:
            response = await self.provider.analyze_image(
                VISION_PROMPT, f"data:{media_type};base64,{data}"
            )
            log_usage(
                feature="vision", request_id=request_id, usage=response.usage, latency_ms=elapsed()
            )
        return VisionResponse(
            analysis=response.text,
            filename=filename,
            media_type=media_type,
            usage=response.usage,
            request_id=request_id,
        )
