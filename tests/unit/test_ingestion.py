from pathlib import Path

from helpdesk.cli import build_pdfs
from helpdesk.ingestion.pipeline import hash_documents


def test_pdf_hash_uses_extracted_content_instead_of_binary_metadata(tmp_path: Path) -> None:
    """Rebuilding equivalent PDFs must not make a compatible index appear stale."""
    source_dir = tmp_path / "source"
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    source_dir.mkdir()
    source = source_dir / "wifi.md"
    source.write_text("# Wi-Fi\n\nForget and reconnect to the network.\n", encoding="utf-8")

    build_pdfs(source_dir, first_dir)
    build_pdfs(source_dir, second_dir)

    assert hash_documents(first_dir) == hash_documents(second_dir)

    source.write_text("# Wi-Fi\n\nEscalate repeated adapter failures.\n", encoding="utf-8")
    build_pdfs(source_dir, second_dir)
    assert hash_documents(first_dir) != hash_documents(second_dir)
