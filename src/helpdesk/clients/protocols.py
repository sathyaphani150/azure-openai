from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from helpdesk.schemas import UsageInfo


@dataclass(slots=True)
class AITextResponse:
    """Provider-independent text response and optional token usage."""

    text: str
    usage: UsageInfo | None = None


class AIProvider(Protocol):
    """Contract implemented by Azure OpenAI and the deterministic offline provider."""

    async def embed(self, texts: list[str]) -> tuple[list[list[float]], UsageInfo | None]: ...

    async def chat(
        self,
        messages: list[dict[str, object]],
        *,
        deployment: str | None = None,
        max_tokens: int = 900,
        temperature: float = 0.1,
        response_format: dict[str, str] | None = None,
    ) -> AITextResponse: ...

    async def analyze_image(
        self, prompt: str, image_data_url: str, *, max_tokens: int = 900
    ) -> AITextResponse: ...

    async def close(self) -> None: ...
