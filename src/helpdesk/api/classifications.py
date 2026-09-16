from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from helpdesk.dependencies import classification_from
from helpdesk.schemas import ClassificationComparisonResponse, ClassificationRequest
from helpdesk.services.classification import ClassificationService

router = APIRouter(prefix="/api/classifications", tags=["classification"])


@router.post("/compare", response_model=ClassificationComparisonResponse)
async def compare_classification(
    body: ClassificationRequest,
    request: Request,
    service: ClassificationService = Depends(classification_from),
) -> ClassificationComparisonResponse:
    """Compare zero-shot and few-shot categorization of an IT issue."""
    return await service.compare(body.issue, request.state.request_id)
