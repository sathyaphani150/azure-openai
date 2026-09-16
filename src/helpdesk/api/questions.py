from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from helpdesk.dependencies import rag_from
from helpdesk.schemas import AnswerResponse, QuestionRequest
from helpdesk.services.rag import RAGService

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.post("", response_model=AnswerResponse)
async def ask_question(
    body: QuestionRequest, request: Request, service: RAGService = Depends(rag_from)
) -> AnswerResponse:
    """Answer an employee question using the grounded RAG pipeline."""
    return await service.answer(body.question, request.state.request_id)
