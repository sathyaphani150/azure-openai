import logging
from uuid import uuid4

from helpdesk.clients.protocols import AIProvider
from helpdesk.observability.usage import elapsed_timer, log_usage, merge_usage
from helpdesk.prompts.rag import RAG_SYSTEM_PROMPT, build_rag_user_prompt
from helpdesk.schemas import AnswerResponse
from helpdesk.services.retrieval import RetrievalService, format_context, source_references

logger = logging.getLogger(__name__)

WEB_FALLBACK_NOTICE = (
    "No relevant information was found in the internal IT knowledge base. "
    "I searched the web for additional information that may help."
)


class RAGService:
    """Generate grounded IT answers from retrieved knowledge-base context or web-search fallback."""

    def __init__(self, provider: AIProvider, retrieval: RetrievalService):
        self.provider = provider
        self.retrieval = retrieval

    async def answer(self, question: str, request_id: str | None = None) -> AnswerResponse:
        """Answer a question using internal KB context, or fallback to web search when KB hit is missing."""
        request_id = request_id or str(uuid4())
        with elapsed_timer() as elapsed:
            results, embedding_usage = await self.retrieval.retrieve(question)
            if not results:
                try:
                    web_resp = await self.provider.web_search(question)
                    usage = merge_usage(embedding_usage, web_resp.usage)
                    log_usage(
                        feature="rag_web_fallback",
                        request_id=request_id,
                        usage=usage,
                        latency_ms=elapsed(),
                    )
                    text_lower = (web_resp.text or "").lower()
                    if (
                        not web_resp.text
                        or "could not find reliable information" in text_lower
                        or "no reliable information" in text_lower
                    ):
                        answer = (
                            f"{WEB_FALLBACK_NOTICE}\n\n"
                            "I could not find reliable information on the web for your query. "
                            "Please contact IT Support."
                        )
                        return AnswerResponse(
                            answer=answer,
                            grounded=False,
                            sources=[],
                            usage=usage,
                            request_id=request_id,
                        )

                    answer = f"{WEB_FALLBACK_NOTICE}\n\n{web_resp.text}"
                    return AnswerResponse(
                        answer=answer,
                        grounded=True,
                        sources=web_resp.sources,
                        usage=usage,
                        request_id=request_id,
                    )
                except Exception as exc:
                    logger.warning("Web search fallback failed: %s", exc)
                    usage = embedding_usage
                    log_usage(
                        feature="rag_web_fallback_error",
                        request_id=request_id,
                        usage=usage,
                        latency_ms=elapsed(),
                    )
                    answer = (
                        f"{WEB_FALLBACK_NOTICE}\n\n"
                        "Web search is currently unavailable and no relevant information was found "
                        "in the internal IT knowledge base. Please contact IT Support."
                    )
                    return AnswerResponse(
                        answer=answer,
                        grounded=False,
                        sources=[],
                        usage=usage,
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

