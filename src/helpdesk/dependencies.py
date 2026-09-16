from __future__ import annotations

from fastapi import Request

from helpdesk.clients.factory import create_ai_provider
from helpdesk.clients.protocols import AIProvider
from helpdesk.config import Settings
from helpdesk.retrieval.vector_store import LocalVectorStore
from helpdesk.services.classification import ClassificationService
from helpdesk.services.guides import GuideService
from helpdesk.services.rag import RAGService
from helpdesk.services.retrieval import RetrievalService
from helpdesk.services.roles import RoleDemoService
from helpdesk.services.vision import VisionService


def settings_from(request: Request) -> Settings:
    """Resolve application settings from FastAPI state."""
    return request.app.state.settings


def provider_from(request: Request) -> AIProvider:
    """Lazily create and cache the configured AI provider."""
    provider = getattr(request.app.state, "provider", None)
    if provider is None:
        provider = create_ai_provider(settings_from(request))
        request.app.state.provider = provider
    return provider


def vector_store_from(request: Request) -> LocalVectorStore:
    """Lazily load and cache the persisted knowledge-base index."""
    store = getattr(request.app.state, "vector_store", None)
    if store is None:
        store = LocalVectorStore.load(settings_from(request).vector_store_dir)
        request.app.state.vector_store = store
    return store


def retrieval_from(request: Request) -> RetrievalService:
    """Construct the retrieval service for a request."""
    return RetrievalService(
        settings_from(request), provider_from(request), vector_store_from(request)
    )


def rag_from(request: Request) -> RAGService:
    """Construct the grounded question-answering service."""
    return RAGService(provider_from(request), retrieval_from(request))


def guide_from(request: Request) -> GuideService:
    """Construct the troubleshooting-guide service."""
    return GuideService(provider_from(request), retrieval_from(request))


def classification_from(request: Request) -> ClassificationService:
    """Construct the zero-shot and few-shot classification service."""
    return ClassificationService(provider_from(request))


def vision_from(request: Request) -> VisionService:
    """Construct the validated screenshot-analysis service."""
    return VisionService(settings_from(request), provider_from(request))


def roles_from(request: Request) -> RoleDemoService:
    """Construct the prompt-role demonstration service."""
    return RoleDemoService(provider_from(request))
