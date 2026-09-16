from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from helpdesk.dependencies import guide_from
from helpdesk.schemas import GuideRequest, GuideResponse
from helpdesk.services.guides import GuideService

router = APIRouter(prefix="/api/guides", tags=["guides"])


@router.post("", response_model=GuideResponse)
async def generate_guide(
    body: GuideRequest, request: Request, service: GuideService = Depends(guide_from)
) -> GuideResponse:
    """Generate a knowledge-base-grounded troubleshooting guide."""
    return await service.generate(body.issue, request.state.request_id)
