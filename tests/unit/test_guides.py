from __future__ import annotations

from helpdesk.clients.protocols import AITextResponse
from helpdesk.ingestion.models import DocumentChunk
from helpdesk.retrieval.vector_store import SearchResult
from helpdesk.schemas import UsageInfo
from helpdesk.services.guides import GUIDE_COMPLETION_TOKEN_BUDGET, GuideService


class _RecordingProvider:
    """Minimal provider double that records guide chat options."""

    def __init__(self) -> None:
        self.chat_max_tokens: int | None = None

    async def chat(
        self,
        messages: list[dict[str, object]],
        *,
        deployment: str | None = None,
        max_tokens: int = 900,
        temperature: float = 0.1,
        response_format: dict[str, str] | None = None,
    ) -> AITextResponse:
        del messages, deployment, temperature, response_format
        self.chat_max_tokens = max_tokens
        return AITextResponse(
            text="## Summary\n\nUse the cited VPN procedure. [vpn.pdf, page 1]",
            usage=UsageInfo(prompt_tokens=10, completion_tokens=12, total_tokens=22),
        )

    async def embed(self, texts: list[str]) -> tuple[list[list[float]], UsageInfo | None]:
        del texts
        return [[1.0]], UsageInfo(prompt_tokens=3, total_tokens=3)

    async def analyze_image(
        self, prompt: str, image_data_url: str, *, max_tokens: int = 900
    ) -> AITextResponse:
        del prompt, image_data_url, max_tokens
        return AITextResponse(text="")

    async def close(self) -> None:
        return None


class _Retrieval:
    """Retrieval double that preserves the guide RAG flow."""

    async def retrieve(self, query: str) -> tuple[list[SearchResult], UsageInfo]:
        del query
        return [
            SearchResult(
                chunk=DocumentChunk(
                    id="vpn-1",
                    source="vpn.pdf",
                    page=1,
                    chunk_index=0,
                    text="If VPN fails, verify network connectivity and credential freshness.",
                    token_count=10,
                ),
                score=0.91,
            )
        ], UsageInfo(prompt_tokens=3, total_tokens=3)


async def test_guide_generation_uses_larger_gpt5_completion_budget() -> None:
    """Guide generation reserves enough GPT-5 budget while preserving citations and usage."""
    provider = _RecordingProvider()

    response = await GuideService(provider, _Retrieval()).generate("VPN fails", "request-1")  # type: ignore[arg-type]

    assert provider.chat_max_tokens == GUIDE_COMPLETION_TOKEN_BUDGET
    assert response.grounded is True
    assert response.sources[0].source == "vpn.pdf"
    assert response.usage is not None
    assert response.usage.prompt_tokens == 13
    assert response.usage.completion_tokens == 12
