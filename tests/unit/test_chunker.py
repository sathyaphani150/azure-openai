from helpdesk.ingestion.chunker import TokenChunker
from helpdesk.ingestion.models import PageText


def test_chunker_is_deterministic_and_keeps_metadata() -> None:
    page = PageText(source="vpn.pdf", page=3, text="VPN connection check. " * 80)
    chunker = TokenChunker(size=100, overlap=20)
    first = chunker.chunk_pages([page])
    second = chunker.chunk_pages([page])
    assert len(first) > 1
    assert [chunk.id for chunk in first] == [chunk.id for chunk in second]
    assert all(chunk.source == "vpn.pdf" and chunk.page == 3 for chunk in first)
    assert all(chunk.token_count <= 100 for chunk in first)
