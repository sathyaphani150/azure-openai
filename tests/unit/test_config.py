from pathlib import Path

import pytest

from helpdesk.config import Settings


def test_fake_provider_needs_no_azure_values(tmp_path: Path) -> None:
    settings = Settings(
        ai_provider="fake",
        knowledge_base_dir=tmp_path / "kb",
        vector_store_dir=tmp_path / "vectors",
    )
    assert settings.azure_missing_values() == []
    assert settings.public_status()["azure_configured"] is True


def test_azure_provider_reports_missing_values() -> None:
    settings = Settings(ai_provider="azure", _env_file=None)
    missing = settings.azure_missing_values()
    assert "AZURE_OPENAI_ENDPOINT" in missing
    assert "AZURE_OPENAI_API_KEY" in missing


def test_chunk_overlap_must_be_smaller_than_size() -> None:
    with pytest.raises(ValueError, match="CHUNK_OVERLAP"):
        Settings(chunk_size_tokens=100, chunk_overlap_tokens=100, _env_file=None)


def test_partial_service_principal_configuration_is_reported() -> None:
    settings = Settings(
        ai_provider="azure",
        azure_openai_endpoint="https://resource.invalid",
        azure_openai_api_version="test-version",
        azure_openai_auth_mode="entra_id",
        azure_openai_chat_deployment="chat",
        azure_openai_embedding_deployment="embedding",
        azure_tenant_id="tenant",
        _env_file=None,
    )
    missing = settings.azure_missing_values()
    assert "AZURE_CLIENT_ID" in missing
    assert "AZURE_CLIENT_SECRET" in missing
