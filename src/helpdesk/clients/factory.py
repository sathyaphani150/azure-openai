from __future__ import annotations

from helpdesk.clients.azure_openai import AzureOpenAIProvider
from helpdesk.clients.fakes import FakeAIProvider
from helpdesk.clients.protocols import AIProvider
from helpdesk.config import Settings


def create_ai_provider(settings: Settings) -> AIProvider:
    """Create the configured AI provider without embedding credentials in callers."""
    if settings.ai_provider == "fake":
        return FakeAIProvider()
    return AzureOpenAIProvider(settings)
