from pathlib import Path

import numpy as np
from fastapi.testclient import TestClient

from helpdesk.cli import build_pdfs
from helpdesk.config import Settings
from helpdesk.ingestion.models import DocumentChunk
from helpdesk.main import create_app
from helpdesk.retrieval.vector_store import (
    INDEX_MANIFEST_VERSION,
    IndexManifest,
    LocalVectorStore,
)


def _app(tmp_path: Path):
    vector_dir = tmp_path / "vectors"
    chunk = DocumentChunk(
        id="vpn1",
        source="vpn-troubleshooting.pdf",
        page=1,
        chunk_index=0,
        text="VPN connection failures can be caused by unstable internet or expired credentials.",
        token_count=12,
    )
    # Fake provider has 256 dimensions; the query still clears a deliberately permissive test threshold.
    vectors = np.zeros((1, 256), dtype=np.float32)
    vectors[0, 0] = 1
    store = LocalVectorStore(
        [chunk],
        vectors,
        IndexManifest(
            INDEX_MANIFEST_VERSION,
            "pending",
            256,
            "fake",
            "deterministic-fake-v2",
            500,
            75,
            {},
            1,
        ),
    )
    store.save(vector_dir)
    settings = Settings(
        ai_provider="fake",
        vector_store_dir=vector_dir,
        knowledge_base_dir=tmp_path / "kb",
        retrieval_min_score=0.15,
        _env_file=None,
    )
    return create_app(settings)


def test_health_and_status_work_without_azure(tmp_path: Path) -> None:
    with TestClient(_app(tmp_path)) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/ready").json()["status"] == "ready"
        assert client.get("/api/config/status").json()["provider"] == "fake"


def test_api_documentation_assets_are_allowed_by_csp(tmp_path: Path) -> None:
    """Swagger and ReDoc must not be blank because their required CDN assets are blocked."""
    with TestClient(_app(tmp_path)) as client:
        docs = client.get("/docs")
        redoc = client.get("/redoc")
        home = client.get("/")

    assert docs.status_code == 200
    assert "SwaggerUIBundle" in docs.text
    assert "https://cdn.jsdelivr.net" in docs.headers["content-security-policy"]
    assert redoc.status_code == 200
    assert "https://cdn.jsdelivr.net" in redoc.headers["content-security-policy"]
    assert "https://cdn.jsdelivr.net" not in home.headers["content-security-policy"]


def test_question_returns_grounded_sources(tmp_path: Path) -> None:
    with TestClient(_app(tmp_path)) as client:
        response = client.post("/api/questions", json={"question": "Why does my VPN fail?"})
    assert response.status_code == 200
    body = response.json()
    assert body["grounded"] is True
    assert body["sources"][0]["source"] == "vpn-troubleshooting.pdf"
    assert response.headers["x-request-id"]


def test_unrelated_question_uses_no_answer_path(tmp_path: Path) -> None:
    with TestClient(_app(tmp_path)) as client:
        response = client.post(
            "/api/questions",
            json={"question": "What is the reimbursement rule for overseas business travel?"},
        )
    assert response.status_code == 200
    assert response.json()["grounded"] is False
    assert response.json()["sources"] == []
    assert "contact IT Support" in response.json()["answer"]


def test_classification_comparison_endpoint(tmp_path: Path) -> None:
    with TestClient(_app(tmp_path)) as client:
        response = client.post(
            "/api/classifications/compare", json={"issue": "My laptop battery is swollen"}
        )
    assert response.status_code == 200
    assert response.json()["few_shot"]["category"] == "Laptop"


def test_guide_and_role_endpoints(tmp_path: Path) -> None:
    """Guide generation and explicit role demonstration work through HTTP."""
    with TestClient(_app(tmp_path)) as client:
        guide = client.post("/api/guides", json={"issue": "VPN tunnel failure"})
        roles = client.post(
            "/api/prompts/roles/demo",
            json={"question": "What should I include when contacting support?"},
        )
    assert guide.status_code == 200
    assert guide.json()["grounded"] is True
    assert [message["role"] for message in roles.json()["messages"]] == [
        "system",
        "user",
        "assistant",
        "user",
    ]


def test_invalid_screenshot_has_controlled_error(tmp_path: Path) -> None:
    """The upload endpoint rejects invalid bytes with the public error envelope."""
    with TestClient(_app(tmp_path)) as client:
        response = client.post(
            "/api/screenshots/analyze",
            files={"image": ("error.txt", b"not an image", "text/plain")},
        )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_validation_errors_have_stable_envelope(tmp_path: Path) -> None:
    with TestClient(_app(tmp_path)) as client:
        response = client.post("/api/questions", json={"question": "x"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "request_validation_error"


def test_startup_auto_ingests_missing_index(tmp_path: Path) -> None:
    """An explicitly enabled single-process deployment builds its index before serving."""
    source_dir = tmp_path / "source"
    pdf_dir = tmp_path / "pdf"
    source_dir.mkdir()
    (source_dir / "vpn.md").write_text(
        "# VPN\n\nCredentials rejected after a password change.\n", encoding="utf-8"
    )
    build_pdfs(source_dir, pdf_dir)
    settings = Settings(
        ai_provider="fake",
        knowledge_base_dir=pdf_dir,
        vector_store_dir=tmp_path / "vectors",
        kb_auto_ingest=True,
        _env_file=None,
    )

    with TestClient(create_app(settings)) as client:
        response = client.get("/ready")
        kb_status = client.get("/api/kb/status").json()

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert kb_status["compatible"] is True
    assert kb_status["documents"] == 1
