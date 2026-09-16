from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from helpdesk.clients.protocols import AIProvider
from helpdesk.config import Settings
from helpdesk.ingestion.chunker import TokenChunker
from helpdesk.ingestion.pdf_extractor import extract_directory, extract_pdf
from helpdesk.retrieval.vector_store import (
    INDEX_MANIFEST_VERSION,
    IndexManifest,
    LocalVectorStore,
)


@dataclass(slots=True)
class IngestionReport:
    """Summary emitted after a successful knowledge-base ingestion."""

    documents: int
    pages: int
    chunks: int
    dimensions: int
    total_tokens: int | None
    vector_store: str


def hash_documents(directory: Path) -> dict[str, str]:
    """Hash normalized extracted content, ignoring unstable PDF file metadata."""
    hashes: dict[str, str] = {}
    for path in sorted(directory.glob("*.pdf")):
        pages = extract_pdf(path)
        canonical = "\n\f\n".join(f"page={page.page}\n{page.text}" for page in pages)
        hashes[path.name] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return hashes


async def ingest_knowledge_base(settings: Settings, provider: AIProvider) -> IngestionReport:
    """Extract, chunk, embed, and persist the configured knowledge base."""
    pages = extract_directory(settings.knowledge_base_dir)
    chunks = TokenChunker(
        size=settings.chunk_size_tokens, overlap=settings.chunk_overlap_tokens
    ).chunk_pages(pages)
    vectors: list[list[float]] = []
    total_usage = 0
    saw_usage = False
    for start in range(0, len(chunks), settings.embedding_batch_size):
        batch = chunks[start : start + settings.embedding_batch_size]
        embedded, usage = await provider.embed([chunk.text for chunk in batch])
        if len(embedded) != len(batch):
            raise ValueError("Embedding provider returned an unexpected number of vectors")
        vectors.extend(embedded)
        if usage and usage.total_tokens is not None:
            saw_usage = True
            total_usage += usage.total_tokens
    matrix = np.asarray(vectors, dtype=np.float32)
    deployment = (
        settings.azure_openai_embedding_deployment
        if settings.ai_provider == "azure"
        else "deterministic-fake-v2"
    )
    manifest = IndexManifest(
        version=INDEX_MANIFEST_VERSION,
        backend="pending",
        dimensions=int(matrix.shape[1]),
        embedding_provider=settings.ai_provider,
        embedding_deployment=deployment or "",
        chunk_size_tokens=settings.chunk_size_tokens,
        chunk_overlap_tokens=settings.chunk_overlap_tokens,
        document_hashes=hash_documents(settings.knowledge_base_dir),
        chunk_count=len(chunks),
    )
    store = LocalVectorStore(chunks, matrix, manifest)
    store.save(settings.vector_store_dir)
    return IngestionReport(
        documents=len({page.source for page in pages}),
        pages=len(pages),
        chunks=len(chunks),
        dimensions=manifest.dimensions,
        total_tokens=total_usage if saw_usage else None,
        vector_store=str(settings.vector_store_dir),
    )
