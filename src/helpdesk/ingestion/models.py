from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class PageText:
    """Text extracted from one source PDF page."""

    source: str
    page: int
    text: str


@dataclass(slots=True)
class DocumentChunk:
    """Token-bounded knowledge-base passage with traceable source metadata."""

    id: str
    source: str
    page: int
    chunk_index: int
    text: str
    token_count: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> DocumentChunk:
        return cls(
            id=str(value["id"]),
            source=str(value["source"]),
            page=int(value["page"]),
            chunk_index=int(value["chunk_index"]),
            text=str(value["text"]),
            token_count=int(value["token_count"]),
        )
