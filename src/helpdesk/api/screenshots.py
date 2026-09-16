from __future__ import annotations

from fastapi import APIRouter, Depends, File, Request, UploadFile

from helpdesk.dependencies import vision_from
from helpdesk.schemas import VisionResponse
from helpdesk.services.vision import VisionService

router = APIRouter(prefix="/api/screenshots", tags=["vision"])


@router.post("/analyze", response_model=VisionResponse)
async def analyze_screenshot(
    request: Request,
    image: UploadFile = File(...),
    service: VisionService = Depends(vision_from),
) -> VisionResponse:
    """Validate and analyze an uploaded IT error screenshot."""
    content = await image.read(service.settings.max_image_bytes + 1)
    return await service.analyze(
        filename=image.filename or "screenshot",
        content=content,
        request_id=request.state.request_id,
    )
