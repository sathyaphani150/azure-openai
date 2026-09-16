from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AppError(Exception):
    """Base exception carrying a safe public API error contract."""

    message: str
    code: str = "application_error"
    status_code: int = 500
    retryable: bool = False
    detail: str | None = None

    def __str__(self) -> str:
        return self.message


class ConfigurationError(AppError):
    """Raised when required runtime configuration is missing or incompatible."""

    def __init__(self, message: str, detail: str | None = None):
        super().__init__(message, "configuration_error", 503, False, detail)


class KnowledgeBaseError(AppError):
    """Raised when knowledge-base extraction or retrieval cannot proceed safely."""

    def __init__(self, message: str, detail: str | None = None):
        super().__init__(message, "knowledge_base_error", 503, False, detail)


class ValidationError(AppError):
    """Raised when uploaded or domain input fails application validation."""

    def __init__(self, message: str, detail: str | None = None):
        super().__init__(message, "validation_error", 422, False, detail)
