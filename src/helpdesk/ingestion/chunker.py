from __future__ import annotations

import hashlib

import tiktoken

from helpdesk.ingestion.models import DocumentChunk, PageText


class TokenChunker:
    """Split extracted pages into deterministic overlapping token chunks."""

    def __init__(self, size: int = 500, overlap: int = 75):
        if size <= 0 or overlap < 0 or overlap >= size:
            raise ValueError("Chunk size must be positive and overlap must be smaller than size")
        self.size = size
        self.overlap = overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def chunk_pages(self, pages: list[PageText]) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for page in pages:
            tokens = self.encoding.encode(page.text)
            start = 0
            chunk_index = 0
            while start < len(tokens):
                end = min(start + self.size, len(tokens))
                text = self.encoding.decode(tokens[start:end]).strip()
                if text:
                    identity = f"{page.source}:{page.page}:{chunk_index}:{text}"
                    chunk_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]
                    chunks.append(
                        DocumentChunk(
                            id=chunk_id,
                            source=page.source,
                            page=page.page,
                            chunk_index=chunk_index,
                            text=text,
                            token_count=end - start,
                        )
                    )
                if end == len(tokens):
                    break
                start = end - self.overlap
                chunk_index += 1
        return chunks
