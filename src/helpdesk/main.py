from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from helpdesk.api import classifications, guides, health, prompt_roles, questions, screenshots
from helpdesk.clients.factory import create_ai_provider
from helpdesk.config import Settings, get_settings
from helpdesk.errors import AppError, ConfigurationError, KnowledgeBaseError
from helpdesk.ingestion.pipeline import ingest_knowledge_base
from helpdesk.retrieval.vector_store import LocalVectorStore
from helpdesk.services.retrieval import validate_index_compatibility


class JsonFormatter(logging.Formatter):
    """Format operational and usage logs as machine-readable JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for name in (
            "request_id",
            "feature",
            "latency_ms",
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
        ):
            if hasattr(record, name):
                payload[name] = getattr(record, name)
        return json.dumps(payload, default=str)


def configure_logging(level: str) -> None:
    """Configure process logging without including prompts, images, or credentials."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())


def content_security_policy(path: str) -> str:
    """Return a strict policy, allowing FastAPI's CDN assets only on API documentation pages."""
    if path in {"/docs", "/docs/oauth2-redirect", "/redoc"}:
        return (
            "default-src 'self'; "
            "connect-src 'self'; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net"
        )
    return "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'"


async def prepare_knowledge_base(app: FastAPI, settings: Settings) -> None:
    """Load a compatible index, rebuilding it at startup when explicitly enabled."""
    if not settings.kb_auto_ingest:
        return
    missing = settings.azure_missing_values() if settings.ai_provider == "azure" else []
    if missing:
        raise ConfigurationError(
            "Automatic knowledge-base ingestion cannot start until Azure configuration is complete."
        )

    provider = create_ai_provider(settings)
    app.state.provider = provider
    try:
        store = LocalVectorStore.load(settings.vector_store_dir)
        validate_index_compatibility(settings, store)
        app.state.vector_store = store
        logging.getLogger(__name__).info("knowledge_base_index_compatible")
    except KnowledgeBaseError:
        report = await ingest_knowledge_base(settings, provider)
        store = LocalVectorStore.load(settings.vector_store_dir)
        validate_index_compatibility(settings, store)
        app.state.vector_store = store
        logging.getLogger(__name__).info(
            "knowledge_base_ingested",
            extra={"feature": "ingestion", "total_tokens": report.total_tokens},
        )


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application, allowing settings injection for offline tests."""
    resolved = settings or get_settings()
    configure_logging(resolved.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        try:
            await prepare_knowledge_base(app, resolved)
        except AppError as exc:
            app.state.startup_error = exc.message
            logging.getLogger(__name__).error("knowledge_base_startup_failed: %s", exc.message)
        except Exception:
            app.state.startup_error = "Knowledge-base startup preparation failed."
            logging.getLogger(__name__).exception("knowledge_base_startup_failed")
        yield
        provider = getattr(app.state, "provider", None)
        if provider is not None:
            await provider.close()

    app = FastAPI(
        title=resolved.app_name,
        version=resolved.app_version,
        description="Grounded IT support using Azure OpenAI, RAG, vision, and prompt engineering.",
        lifespan=lifespan,
    )
    app.state.settings = resolved
    app.state.provider = None
    app.state.vector_store = None
    app.state.startup_error = None

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request.state.request_id = request.headers.get("x-request-id") or str(uuid4())
        response = await call_next(request)
        response.headers["x-request-id"] = request.state.request_id
        response.headers["x-content-type-options"] = "nosniff"
        response.headers["x-frame-options"] = "DENY"
        response.headers["referrer-policy"] = "no-referrer"
        response.headers["content-security-policy"] = content_security_policy(request.url.path)
        return response

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "retryable": exc.retryable,
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        del exc
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "request_validation_error",
                    "message": "The request contains missing or invalid fields.",
                    "retryable": False,
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logging.getLogger(__name__).exception(
            "unhandled_request_error",
            extra={"request_id": getattr(request.state, "request_id", None)},
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred.",
                    "retryable": False,
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    for router in (
        health.router,
        questions.router,
        screenshots.router,
        guides.router,
        classifications.router,
        prompt_roles.router,
    ):
        app.include_router(router)

    web_root = Path(__file__).parent / "web"
    app.mount("/static", StaticFiles(directory=web_root / "static"), name="static")

    @app.get("/", include_in_schema=False)
    async def web_ui() -> FileResponse:
        return FileResponse(web_root / "templates" / "index.html")

    return app


app = create_app()
