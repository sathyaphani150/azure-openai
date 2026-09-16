from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated runtime configuration loaded from environment variables or `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Azure OpenAI IT Helpdesk"
    app_version: str = "0.1.0"
    ai_provider: Literal["azure", "fake"] = "azure"

    azure_openai_endpoint: str | None = None
    azure_openai_api_version: str | None = None
    azure_openai_auth_mode: Literal["api_key", "entra_id"] = "api_key"
    azure_openai_api_key: SecretStr | None = None
    azure_openai_chat_deployment: str | None = None
    azure_openai_embedding_deployment: str | None = None
    azure_openai_vision_deployment: str | None = None
    azure_tenant_id: str | None = None
    azure_client_id: str | None = None
    azure_client_secret: SecretStr | None = None

    knowledge_base_dir: Path = Path("knowledge-base/pdf")
    vector_store_dir: Path = Path("data/vector-store")
    kb_auto_ingest: bool = False
    chunk_size_tokens: int = Field(default=500, ge=100, le=4000)
    chunk_overlap_tokens: int = Field(default=75, ge=0, le=1000)
    retrieval_top_k: int = Field(default=5, ge=1, le=20)
    retrieval_min_score: float = Field(default=0.15, ge=-1, le=1)
    embedding_batch_size: int = Field(default=16, ge=1, le=128)

    azure_max_retries: int = Field(default=3, ge=0, le=8)
    azure_request_timeout_seconds: float = Field(default=45, ge=1, le=180)
    max_image_bytes: int = Field(default=5 * 1024 * 1024, ge=1024)
    max_image_pixels: int = Field(default=20_000_000, ge=1_000_000)
    log_level: str = "INFO"

    @field_validator("chunk_overlap_tokens")
    @classmethod
    def overlap_is_nonnegative(cls, value: int) -> int:
        return value

    def model_post_init(self, __context: object) -> None:
        if self.chunk_overlap_tokens >= self.chunk_size_tokens:
            raise ValueError("CHUNK_OVERLAP_TOKENS must be smaller than CHUNK_SIZE_TOKENS")

    def azure_missing_values(self, *, feature: str | None = None) -> list[str]:
        if self.ai_provider == "fake":
            return []
        required: dict[str, object | None] = {
            "AZURE_OPENAI_ENDPOINT": self.azure_openai_endpoint,
            "AZURE_OPENAI_API_VERSION": self.azure_openai_api_version,
            "AZURE_OPENAI_CHAT_DEPLOYMENT": self.azure_openai_chat_deployment,
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": self.azure_openai_embedding_deployment,
        }
        if feature == "vision":
            required["AZURE_OPENAI_VISION_DEPLOYMENT"] = self.azure_openai_vision_deployment
        if self.azure_openai_auth_mode == "api_key":
            required["AZURE_OPENAI_API_KEY"] = self.azure_openai_api_key
        elif self.azure_tenant_id or self.azure_client_secret:
            required.update(
                {
                    "AZURE_TENANT_ID": self.azure_tenant_id,
                    "AZURE_CLIENT_ID": self.azure_client_id,
                    "AZURE_CLIENT_SECRET": self.azure_client_secret,
                }
            )
        return [name for name, value in required.items() if not value]

    def public_status(self) -> dict[str, object]:
        return {
            "provider": self.ai_provider,
            "auth_mode": self.azure_openai_auth_mode,
            "azure_configured": not self.azure_missing_values(),
            "vision_configured": not self.azure_missing_values(feature="vision"),
            "chat_deployment_configured": bool(self.azure_openai_chat_deployment),
            "embedding_deployment_configured": bool(self.azure_openai_embedding_deployment),
            "vision_deployment_configured": bool(self.azure_openai_vision_deployment),
            "entra_service_principal_configured": bool(
                self.azure_tenant_id and self.azure_client_id and self.azure_client_secret
            ),
            "knowledge_base_auto_ingest": self.kb_auto_ingest,
        }


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()
