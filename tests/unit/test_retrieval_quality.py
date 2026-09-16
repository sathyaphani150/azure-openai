from pathlib import Path

import numpy as np
import pytest

from helpdesk.clients.fakes import FakeAIProvider
from helpdesk.config import Settings
from helpdesk.ingestion.models import DocumentChunk
from helpdesk.retrieval.vector_store import (
    INDEX_MANIFEST_VERSION,
    IndexManifest,
    LocalVectorStore,
)
from helpdesk.services.retrieval import RetrievalService


RUNBOOK_FIXTURES = [
    (
        "vpn-troubleshooting.pdf",
        "VPN tunnel remote access gateway error 809 internal file share timeout connection failure.",
    ),
    (
        "wifi-troubleshooting.pdf",
        "Wi-Fi wifi wireless laptop network adapter no networks visible connected no internet slow wireless.",
    ),
    (
        "password-reset.pdf",
        "Password account lock credentials sign-in MFA expired password repeated attempts old credentials.",
    ),
    (
        "laptop-troubleshooting.pdf",
        "Laptop battery overheat swollen hot screen blank keyboard touchpad startup display issue.",
    ),
    (
        "software-installation.pdf",
        "Software install application update administrator permissions approved software error 1603 reinstall.",
    ),
    (
        "microsoft-365-troubleshooting.pdf",
        "Outlook Teams Microsoft 365 OneDrive disconnected web mail sync conflict sign-in.",
    ),
    (
        "it-support-policy.pdf",
        "Support ticket information raise a ticket support hours device support approved software policy.",
    ),
]


async def _fake_quality_store(tmp_path: Path) -> tuple[Settings, LocalVectorStore]:
    """Create an isolated vector store whose manifest matches the fake provider."""
    provider = FakeAIProvider()
    chunks = [
        DocumentChunk(
            id=f"chunk-{index}",
            source=source,
            page=1,
            chunk_index=0,
            text=text,
            token_count=len(text.split()),
        )
        for index, (source, text) in enumerate(RUNBOOK_FIXTURES)
    ]
    vectors, _ = await provider.embed([chunk.text for chunk in chunks])
    settings = Settings(
        ai_provider="fake",
        knowledge_base_dir=tmp_path / "nonexistent-kb",
        vector_store_dir=tmp_path / "vectors",
        _env_file=None,
    )
    store = LocalVectorStore(
        chunks,
        np.asarray(vectors, dtype=np.float32),
        IndexManifest(
            version=INDEX_MANIFEST_VERSION,
            backend="pending",
            dimensions=provider.dimension,
            embedding_provider="fake",
            embedding_deployment="deterministic-fake-v2",
            chunk_size_tokens=settings.chunk_size_tokens,
            chunk_overlap_tokens=settings.chunk_overlap_tokens,
            document_hashes={},
            chunk_count=len(chunks),
        ),
    )
    store.save(settings.vector_store_dir)
    return settings, LocalVectorStore.load(settings.vector_store_dir)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("question", "expected_source"),
    [
        ("The VPN shows error 809 and cannot reach the gateway", "vpn-troubleshooting.pdf"),
        ("VPN connects but an internal file share times out", "vpn-troubleshooting.pdf"),
        ("No wireless networks appear on my laptop", "wifi-troubleshooting.pdf"),
        ("Wi-Fi is connected but there is no internet", "wifi-troubleshooting.pdf"),
        ("My password account is locked after repeated attempts", "password-reset.pdf"),
        ("My password changed but old credentials keep prompting", "password-reset.pdf"),
        ("The laptop battery is swollen and unusually hot", "laptop-troubleshooting.pdf"),
        ("My laptop powers on but the screen stays blank", "laptop-troubleshooting.pdf"),
        ("Approved software installation fails with error 1603", "software-installation.pdf"),
        ("Software update says administrator permissions required", "software-installation.pdf"),
        ("Outlook is disconnected but web mail works", "microsoft-365-troubleshooting.pdf"),
        ("OneDrive has a file sync conflict", "microsoft-365-troubleshooting.pdf"),
        ("What information is required to raise a support ticket?", "it-support-policy.pdf"),
    ],
)
async def test_diverse_questions_retrieve_expected_runbook(
    tmp_path: Path, question: str, expected_source: str
) -> None:
    """Representative issue variants retrieve the intended controlled runbook."""
    settings, store = await _fake_quality_store(tmp_path)
    results, _ = await RetrievalService(settings, FakeAIProvider(), store).retrieve(question)
    assert results
    assert results[0].chunk.source == expected_source
