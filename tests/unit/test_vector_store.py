from pathlib import Path

import numpy as np

from helpdesk.ingestion.models import DocumentChunk
from helpdesk.retrieval.vector_store import (
    INDEX_MANIFEST_VERSION,
    IndexManifest,
    LocalVectorStore,
)


def _chunk(identifier: str, text: str) -> DocumentChunk:
    return DocumentChunk(identifier, f"{identifier}.pdf", 1, 0, text, 2)


def test_vector_store_search_and_round_trip(tmp_path: Path) -> None:
    chunks = [_chunk("vpn", "vpn tunnel"), _chunk("wifi", "wireless network")]
    vectors = np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    manifest = IndexManifest(
        INDEX_MANIFEST_VERSION, "pending", 2, "fake", "fake", 100, 10, {}, 2
    )
    store = LocalVectorStore(chunks, vectors, manifest)
    store.save(tmp_path)

    loaded = LocalVectorStore.load(tmp_path)
    results = loaded.search([0.9, 0.1], top_k=2)
    assert results[0].chunk.id == "vpn"
    assert results[0].score > results[1].score
