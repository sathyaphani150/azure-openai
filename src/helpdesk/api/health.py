from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from helpdesk.config import Settings
from helpdesk.errors import KnowledgeBaseError
from helpdesk.retrieval.vector_store import LocalVectorStore
from helpdesk.services.retrieval import validate_index_compatibility

router = APIRouter(tags=["system"])


@router.get("/health")
async def health(request: Request) -> dict[str, object]:
    """Report process health without contacting Azure or exposing configuration."""
    settings = request.app.state.settings
    return {"status": "ok", "application": settings.app_name, "version": settings.app_version}


@router.get("/ready")
async def ready(request: Request) -> JSONResponse:
    """Report whether provider configuration and the vector index are ready."""
    settings = request.app.state.settings
    missing = settings.azure_missing_values() if settings.ai_provider == "azure" else []
    index_status = inspect_knowledge_base(settings)
    startup_error = getattr(request.app.state, "startup_error", None)
    ready_state = not missing and index_status["compatible"] and not startup_error
    content = {
        "status": "ready" if ready_state else "degraded",
        "provider_configured": not missing,
        "knowledge_base_indexed": index_status["indexed"],
        "knowledge_base_compatible": index_status["compatible"],
        "knowledge_base_reason": index_status.get("reason"),
        "missing_configuration": missing,
        "startup_error": startup_error,
    }
    return JSONResponse(status_code=200 if ready_state else 503, content=content)


@router.get("/api/config/status")
async def config_status(request: Request) -> dict[str, object]:
    """Return secret-safe provider configuration status."""
    return request.app.state.settings.public_status()


@router.get("/api/kb/status")
async def knowledge_base_status(request: Request) -> dict[str, object]:
    """Return the persisted knowledge-base index summary."""
    settings = request.app.state.settings
    status = inspect_knowledge_base(settings)
    if not status["compatible"]:
        return status
    store = LocalVectorStore.load(settings.vector_store_dir)
    return {
        **status,
        "documents": len(store.manifest.document_hashes),
        "chunks": store.manifest.chunk_count,
        "provider": store.manifest.embedding_provider,
        "backend": store.manifest.backend,
    }


def inspect_knowledge_base(settings: Settings) -> dict[str, object]:
    """Return a secret-safe view of index presence and runtime compatibility."""
    try:
        store = LocalVectorStore.load(settings.vector_store_dir)
        validate_index_compatibility(settings, store)
        return {"indexed": True, "compatible": True, "reason": None}
    except KnowledgeBaseError as exc:
        indexed = (settings.vector_store_dir / "manifest.json").is_file()
        return {
            "indexed": indexed,
            "compatible": False,
            "reason": exc.message,
            "documents": 0,
            "chunks": 0,
        }
