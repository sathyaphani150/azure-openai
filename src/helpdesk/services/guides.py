from __future__ import annotations

from uuid import uuid4

from helpdesk.clients.protocols import AIProvider
from helpdesk.observability.usage import elapsed_timer, log_usage, merge_usage
from helpdesk.prompts.guide import GUIDE_SYSTEM_PROMPT, build_guide_prompt
from helpdesk.schemas import GuideResponse
from helpdesk.services.retrieval import RetrievalService, format_context, source_references

GUIDE_COMPLETION_TOKEN_BUDGET = 3000
"""Completion budget for GPT-5 guide output, including hidden reasoning tokens."""


class GuideService:
    """Create structured troubleshooting guides grounded in retrieved content."""

    def __init__(self, provider: AIProvider, retrieval: RetrievalService):
        self.provider = provider
        self.retrieval = retrieval

    async def generate(self, issue: str, request_id: str | None = None) -> GuideResponse:
        """Generate a cited guide or an explicit no-result response."""
        request_id = request_id or str(uuid4())
        with elapsed_timer() as elapsed:
            results, embedding_usage = await self.retrieval.retrieve(issue)
            if not results:
                log_usage(
                    feature="guide",
                    request_id=request_id,
                    usage=embedding_usage,
                    latency_ms=elapsed(),
                )
                return GuideResponse(
                    guide=(
                        "No relevant knowledge-base guidance was found. Contact IT Support with the "
                        "error details and do not attempt unverified administrative changes."
                    ),
                    grounded=False,
                    sources=[],
                    usage=embedding_usage,
                    request_id=request_id,
                )
            response = await self.provider.chat(
                [
                    {"role": "system", "content": GUIDE_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": build_guide_prompt(issue, format_context(results)),
                    },
                ],
                max_tokens=GUIDE_COMPLETION_TOKEN_BUDGET,
            )
            usage = merge_usage(embedding_usage, response.usage)
            log_usage(feature="guide", request_id=request_id, usage=usage, latency_ms=elapsed())
            return GuideResponse(
                guide=response.text,
                grounded=True,
                sources=source_references(results),
                usage=usage,
                request_id=request_id,
            )
