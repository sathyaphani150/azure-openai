import pytest
from unittest.mock import AsyncMock, MagicMock

from helpdesk.clients.fakes import FakeAIProvider
from helpdesk.clients.protocols import AIWebSearchResponse
from helpdesk.schemas import SourceReference, UsageInfo
from helpdesk.services.rag import RAGService, WEB_FALLBACK_NOTICE
from helpdesk.services.retrieval import RetrievalService
from helpdesk.retrieval.vector_store import SearchResult
from helpdesk.ingestion.models import DocumentChunk


@pytest.mark.asyncio
async def test_kb_hit_uses_existing_rag_path() -> None:
    """When KB retrieval succeeds, the existing RAG chat path is executed without web search."""
    provider = FakeAIProvider()
    retrieval = MagicMock(spec=RetrievalService)
    
    chunk = DocumentChunk(
        id="test-1",
        source="vpn-troubleshooting.pdf",
        page=1,
        chunk_index=0,
        text="KNOWLEDGE-BASE CONTEXT: VPN instructions...",
        token_count=10,
    )
    retrieval.retrieve = AsyncMock(
        return_value=([SearchResult(chunk=chunk, score=0.95)], UsageInfo(total_tokens=10))
    )

    service = RAGService(provider, retrieval)
    response = await service.answer("How do I connect to VPN?")

    assert response.grounded is True
    assert response.sources[0].source == "vpn-troubleshooting.pdf"
    assert "No relevant information was found" not in response.answer


@pytest.mark.asyncio
async def test_kb_miss_uses_web_search_fallback() -> None:
    """When KB retrieval finds no results, web search fallback is invoked with required notice."""
    provider = FakeAIProvider()
    retrieval = MagicMock(spec=RetrievalService)
    retrieval.retrieve = AsyncMock(return_value=([], UsageInfo(total_tokens=5)))

    service = RAGService(provider, retrieval)
    response = await service.answer("What is the current policy on remote work stipends?")

    assert response.grounded is True
    assert WEB_FALLBACK_NOTICE in response.answer
    assert response.sources[0].source.startswith("Web Search:")


@pytest.mark.asyncio
async def test_web_search_failure_returns_safe_error_no_hallucination() -> None:
    """When web search fails, a safe message is returned without hallucinated facts or sources."""
    provider = MagicMock()
    provider.web_search = AsyncMock(side_effect=Exception("Web search API connection error"))

    retrieval = MagicMock(spec=RetrievalService)
    retrieval.retrieve = AsyncMock(return_value=([], UsageInfo(total_tokens=5)))

    service = RAGService(provider, retrieval)
    response = await service.answer("Unrelated web_search_fail question")

    assert response.grounded is False
    assert response.sources == []
    assert WEB_FALLBACK_NOTICE in response.answer
    assert "Web search is currently unavailable" in response.answer


@pytest.mark.asyncio
async def test_web_search_unreliable_info_returns_safe_message() -> None:
    """When web search finds no reliable info, explicitly state so instead of guessing."""
    provider = FakeAIProvider()
    retrieval = MagicMock(spec=RetrievalService)
    retrieval.retrieve = AsyncMock(return_value=([], UsageInfo(total_tokens=5)))

    service = RAGService(provider, retrieval)
    response = await service.answer("unreliable query test")

    assert response.grounded is False
    assert response.sources == []
    assert WEB_FALLBACK_NOTICE in response.answer
    assert "could not find reliable information" in response.answer
