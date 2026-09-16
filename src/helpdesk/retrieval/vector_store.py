from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from helpdesk.errors import KnowledgeBaseError
from helpdesk.ingestion.models import DocumentChunk

try:
    import faiss  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - exercised where optional native package is absent
    faiss = None


INDEX_MANIFEST_VERSION = 2
"""Current on-disk index schema and document-fingerprint version."""


@dataclass(slots=True)
class IndexManifest:
    """Metadata required to detect a stale or incompatible vector index."""

    version: int
    backend: str
    dimensions: int
    embedding_provider: str
    embedding_deployment: str
    chunk_size_tokens: int
    chunk_overlap_tokens: int
    document_hashes: dict[str, str]
    chunk_count: int


@dataclass(slots=True)
class SearchResult:
    """A retrieved chunk and its cosine similarity score."""

    chunk: DocumentChunk
    score: float


class LocalVectorStore:
    """Persistent cosine-similarity store using FAISS when installed, NumPy otherwise."""

    def __init__(
        self,
        chunks: list[DocumentChunk],
        vectors: np.ndarray,
        manifest: IndexManifest,
    ):
        if len(chunks) != len(vectors):
            raise ValueError("Chunk and vector counts do not match")
        if vectors.ndim != 2:
            raise ValueError("Vectors must be a two-dimensional matrix")
        self.chunks = chunks
        self.vectors = self._normalize(vectors.astype(np.float32, copy=False))
        self.manifest = manifest
        self._index = None
        if faiss is not None and len(self.vectors):
            self._index = faiss.IndexFlatIP(self.vectors.shape[1])
            self._index.add(self.vectors)

    @staticmethod
    def _normalize(vectors: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        return vectors / norms

    def search(self, query_vector: list[float], top_k: int) -> list[SearchResult]:
        """Return the highest-scoring chunks for a query embedding."""
        if not self.chunks:
            return []
        query = np.asarray([query_vector], dtype=np.float32)
        if query.shape[1] != self.vectors.shape[1]:
            raise KnowledgeBaseError(
                "Query embedding dimensions do not match the knowledge-base index. Re-ingest the PDFs."
            )
        query = self._normalize(query)
        count = min(top_k, len(self.chunks))
        if self._index is not None:
            scores, indices = self._index.search(query, count)
            pairs = zip(indices[0].tolist(), scores[0].tolist(), strict=True)
        else:
            similarities = self.vectors @ query[0]
            indices = np.argsort(-similarities)[:count]
            pairs = ((int(index), float(similarities[index])) for index in indices)
        return [
            SearchResult(chunk=self.chunks[index], score=float(score))
            for index, score in pairs
            if index >= 0
        ]

    def save(self, directory: Path) -> None:
        """Persist normalized vectors, chunks, manifest, and optional FAISS index."""
        directory.mkdir(parents=True, exist_ok=True)
        np.save(directory / "vectors.npy", self.vectors, allow_pickle=False)
        (directory / "chunks.json").write_text(
            json.dumps([chunk.to_dict() for chunk in self.chunks], indent=2), encoding="utf-8"
        )
        backend = "faiss" if self._index is not None else "numpy"
        self.manifest.backend = backend
        (directory / "manifest.json").write_text(
            json.dumps(asdict(self.manifest), indent=2, sort_keys=True), encoding="utf-8"
        )
        if self._index is not None:
            faiss.write_index(self._index, str(directory / "index.faiss"))

    @classmethod
    def load(cls, directory: Path) -> LocalVectorStore:
        """Load and validate a previously persisted index."""
        try:
            manifest_data = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
            chunk_data = json.loads((directory / "chunks.json").read_text(encoding="utf-8"))
            vectors = np.load(directory / "vectors.npy", allow_pickle=False)
            manifest = IndexManifest(**manifest_data)
            chunks = [DocumentChunk.from_dict(item) for item in chunk_data]
            return cls(chunks, vectors, manifest)
        except FileNotFoundError as exc:
            raise KnowledgeBaseError(
                "The knowledge-base index is not available. Run the ingestion command first."
            ) from exc
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            raise KnowledgeBaseError(
                "The knowledge-base index is invalid. Re-ingest the PDFs."
            ) from exc
