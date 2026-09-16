from __future__ import annotations

from uuid import uuid4

from helpdesk.clients.protocols import AIProvider
from helpdesk.observability.usage import elapsed_timer, log_usage, merge_usage
from helpdesk.prompts.rag import RAG_SYSTEM_PROMPT, build_rag_user_prompt
from helpdesk.schemas import AnswerResponse
from helpdesk.services.retrieval import RetrievalService, format_context, source_references


class RAGService:
    """Generate grounded IT answers from retrieved knowledge-base context."""

    def __init__(self, provider: AIProvider, retrieval: RetrievalService):
        self.provider = provider
        self.retrieval = retrieval

    async def answer(self, question: str, request_id: str | None = None) -> AnswerResponse:
        """Answer a question or safely escalate when retrieval is insufficient."""
        request_id = request_id or str(uuid4())
        with elapsed_timer() as elapsed:
            results, embedding_usage = await self.retrieval.retrieve(question)
            if not results:
                answer = (
                    "I could not find sufficiently relevant information in the IT knowledge base. "
                    "Please contact IT Support and include the exact error, affected device or app, "
                    "when the issue began, and troubleshooting already attempted."
                )
                log_usage(
                    feature="rag",
                    request_id=request_id,
                    usage=embedding_usage,
                    latency_ms=elapsed(),
                )
                return AnswerResponse(
                    answer=answer,
                    grounded=False,
                    sources=[],
                    usage=embedding_usage,
                    request_id=request_id,
                )
            response = await self.provider.chat(
                [
                    {"role": "system", "content": RAG_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": build_rag_user_prompt(question, format_context(results)),
                    },
                ]
            )
            usage = merge_usage(embedding_usage, response.usage)
            log_usage(feature="rag", request_id=request_id, usage=usage, latency_ms=elapsed())
            return AnswerResponse(
                answer=response.text,
                grounded=True,
                sources=source_references(results),
                usage=usage,
                request_id=request_id,
            )
