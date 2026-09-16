from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from helpdesk.dependencies import roles_from
from helpdesk.schemas import RoleDemoRequest, RoleDemoResponse
from helpdesk.services.roles import RoleDemoService

router = APIRouter(prefix="/api/prompts/roles", tags=["prompt-engineering"])


@router.post("/demo", response_model=RoleDemoResponse)
async def demonstrate_roles(
    body: RoleDemoRequest,
    request: Request,
    service: RoleDemoService = Depends(roles_from),
) -> RoleDemoResponse:
    """Demonstrate System, User, and Assistant messages."""
    return await service.demonstrate(body.question, request.state.request_id)
