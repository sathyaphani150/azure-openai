from __future__ import annotations

from helpdesk.clients.protocols import AIProvider
from helpdesk.config import Settings
from helpdesk.errors import KnowledgeBaseError
from helpdesk.ingestion.pipeline import hash_documents
from helpdesk.retrieval.vector_store import (
    INDEX_MANIFEST_VERSION,
    LocalVectorStore,
    SearchResult,
)
from helpdesk.schemas import SourceReference, UsageInfo


class RetrievalService:
    """Embed questions and retrieve compatible, relevant knowledge-base chunks."""

    def __init__(self, settings: Settings, provider: AIProvider, store: LocalVectorStore):
        self.settings = settings
        self.provider = provider
        self.store = store
        validate_index_compatibility(settings, store)

    async def retrieve(self, query: str) -> tuple[list[SearchResult], UsageInfo | None]:
        """Return relevant top-k results and the query-embedding token usage."""
        vectors, usage = await self.provider.embed([query])
        results = [
            result
            for result in self.store.search(vectors[0], self.settings.retrieval_top_k)
            if result.score >= self.settings.retrieval_min_score
        ]
        return results, usage


def validate_index_compatibility(settings: Settings, store: LocalVectorStore) -> None:
    """Reject an index that cannot safely serve the current runtime configuration."""
    manifest = store.manifest
    if manifest.version != INDEX_MANIFEST_VERSION:
        raise KnowledgeBaseError(
            "The knowledge-base index format is outdated. Re-ingest the PDFs."
        )
    expected_provider = settings.ai_provider
    if manifest.embedding_provider != expected_provider:
        raise KnowledgeBaseError(
            "The index was built with a different embedding provider. Re-ingest the knowledge base."
        )
    if expected_provider == "azure" and (
        manifest.embedding_deployment != settings.azure_openai_embedding_deployment
    ):
        raise KnowledgeBaseError(
            "The embedding deployment changed. Re-ingest the knowledge base before searching."
        )
    if (
        manifest.chunk_size_tokens != settings.chunk_size_tokens
        or manifest.chunk_overlap_tokens != settings.chunk_overlap_tokens
    ):
        raise KnowledgeBaseError(
            "Chunking settings changed. Re-ingest the knowledge base before searching."
        )
    if manifest.document_hashes and not settings.knowledge_base_dir.exists():
        raise KnowledgeBaseError(
            "The knowledge-base PDF directory is unavailable. Restore it and re-ingest."
        )
    if settings.knowledge_base_dir.exists():
        current_hashes = hash_documents(settings.knowledge_base_dir)
        if current_hashes != manifest.document_hashes:
            raise KnowledgeBaseError(
                "Knowledge-base PDF content changed. Re-ingest it before searching."
            )


def format_context(results: list[SearchResult], max_characters: int = 14_000) -> str:
    """Build bounded model context with source labels preserved."""
    sections: list[str] = []
    length = 0
    for result in results:
        label = f"[{result.chunk.source}, page {result.chunk.page}]"
        section = f"{label}\n{result.chunk.text}"
        if length + len(section) > max_characters:
            break
        sections.append(section)
        length += len(section)
    return "\n\n".join(sections)


def source_references(results: list[SearchResult]) -> list[SourceReference]:
    """Convert internal retrieval hits into API-safe source references."""
    return [
        SourceReference(
            source=result.chunk.source,
            page=result.chunk.page,
            score=round(result.score, 4),
            excerpt=result.chunk.text[:300],
        )
        for result in results
    ]
