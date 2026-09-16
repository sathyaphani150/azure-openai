from __future__ import annotations

import asyncio
import logging
import random
from collections.abc import Awaitable, Callable

import openai
from azure.identity.aio import (
    ClientSecretCredential,
    DefaultAzureCredential,
    get_bearer_token_provider,
)
from openai import AsyncOpenAI

from helpdesk.clients.protocols import AITextResponse
from helpdesk.config import Settings
from helpdesk.errors import AppError, ConfigurationError
from helpdesk.schemas import UsageInfo

logger = logging.getLogger(__name__)


class AzureOpenAIProvider:
    """OpenAI SDK adapter configured for Azure API-key or Microsoft Entra authentication."""

    def __init__(self, settings: Settings):
        missing = settings.azure_missing_values()
        if missing:
            raise ConfigurationError(
                "Azure OpenAI is not configured.",
                f"Set the following environment variables: {', '.join(missing)}",
            )
        self.settings = settings
        self._credential: ClientSecretCredential | DefaultAzureCredential | None = None
        api_key: str | Callable[[], Awaitable[str]]
        if settings.azure_openai_auth_mode == "api_key":
            api_key = settings.azure_openai_api_key.get_secret_value()  # type: ignore[union-attr]
        else:
            if (
                settings.azure_tenant_id
                and settings.azure_client_id
                and settings.azure_client_secret
            ):
                self._credential = ClientSecretCredential(
                    tenant_id=settings.azure_tenant_id,
                    client_id=settings.azure_client_id,
                    client_secret=settings.azure_client_secret.get_secret_value(),
                )
            else:
                credential_options = (
                    {"managed_identity_client_id": settings.azure_client_id}
                    if settings.azure_client_id
                    else {}
                )
                self._credential = DefaultAzureCredential(**credential_options)
            token_provider = get_bearer_token_provider(
                self._credential, "https://ai.azure.com/.default"
            )
            api_key = token_provider
        self.client = AsyncOpenAI(
            base_url=f"{settings.azure_openai_endpoint.rstrip('/')}/openai/v1/",  # type: ignore[union-attr]
            api_key=api_key,
            timeout=settings.azure_request_timeout_seconds,
            max_retries=0,
        )

    @staticmethod
    def _usage(response: object) -> UsageInfo | None:
        usage = getattr(response, "usage", None)
        if not usage:
            return None
        return UsageInfo(
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
            total_tokens=getattr(usage, "total_tokens", None),
        )

    async def _with_retry(self, operation: Callable[[], Awaitable[object]]) -> object:
        attempts = self.settings.azure_max_retries + 1
        for attempt in range(attempts):
            try:
                return await operation()
            except (
                openai.RateLimitError,
                openai.APITimeoutError,
                openai.APIConnectionError,
            ) as exc:
                if attempt + 1 >= attempts:
                    raise self._map_error(exc) from exc
                delay = min(8.0, (2**attempt) + random.uniform(0, 0.25))
                logger.warning("Transient Azure OpenAI error; retrying", extra={"delay": delay})
                await asyncio.sleep(delay)
            except openai.APIError as exc:
                raise self._map_error(exc) from exc
        raise RuntimeError("Retry loop exited unexpectedly")

    @staticmethod
    def _map_error(exc: openai.APIError) -> AppError:
        if isinstance(exc, (openai.AuthenticationError, openai.PermissionDeniedError)):
            return AppError(
                "Azure OpenAI authentication failed. Verify the configured credential and access.",
                "azure_authentication_failed",
                502,
                False,
            )
        if isinstance(exc, openai.NotFoundError):
            return AppError(
                "An Azure OpenAI deployment or endpoint was not found. Verify your configuration.",
                "azure_deployment_not_found",
                502,
                False,
            )
        if isinstance(exc, openai.RateLimitError):
            body = str(exc).lower()
            quota = "quota" in body
            return AppError(
                "Azure OpenAI quota is exhausted. Contact the Azure administrator."
                if quota
                else "Azure OpenAI is rate-limiting requests. Please retry shortly.",
                "azure_quota_exceeded" if quota else "azure_rate_limited",
                503,
                not quota,
            )
        if isinstance(exc, (openai.APITimeoutError, openai.APIConnectionError)):
            return AppError(
                "Azure OpenAI is temporarily unreachable. Please retry.",
                "azure_unavailable",
                503,
                True,
            )
        return AppError(
            "Azure OpenAI could not complete the request.",
            "azure_request_failed",
            502,
            False,
        )

    async def embed(self, texts: list[str]) -> tuple[list[list[float]], UsageInfo | None]:
        deployment = self.settings.azure_openai_embedding_deployment

        async def operation() -> object:
            return await self.client.embeddings.create(model=deployment, input=texts)

        response = await self._with_retry(operation)
        ordered = sorted(response.data, key=lambda item: item.index)  # type: ignore[attr-defined]
        return [item.embedding for item in ordered], self._usage(response)

    async def chat(
        self,
        messages: list[dict[str, object]],
        *,
        deployment: str | None = None,
        max_tokens: int = 900,
        temperature: float = 0.1,
        response_format: dict[str, str] | None = None,
    ) -> AITextResponse:
        model = deployment or self.settings.azure_openai_chat_deployment
        completion_budget = max(max_tokens, 1500)

        async def operation() -> object:
            # GPT-5 uses the same budget for hidden reasoning and visible output.
            kwargs: dict[str, object] = {
                "model": model,
                "messages": messages,
                "max_completion_tokens": completion_budget,
                "reasoning_effort": "low",
            }
            if response_format:
                kwargs["response_format"] = response_format
            return await self.client.chat.completions.create(**kwargs)  # type: ignore[arg-type]

        response = await self._with_retry(operation)
        choices = getattr(response, "choices", None) or []
        choice = choices[0] if choices else None
        message = getattr(choice, "message", None)
        finish_reason = getattr(choice, "finish_reason", None)
        content = getattr(message, "content", None)
        if not content:
            usage = getattr(response, "usage", None)
            completion_details = getattr(usage, "completion_tokens_details", None)
            response_fields = sorted(getattr(response, "model_fields_set", set()))
            choice_fields = sorted(getattr(choice, "model_fields_set", set()))
            message_fields = sorted(getattr(message, "model_fields_set", set()))
            logger.warning(
                "empty_chat_completion model=%r finish_reason=%r choice_count=%d "
                "content_type=%s "
                "content_length=%d refusal_present=%s tool_call_count=%d "
                "prompt_tokens=%r completion_tokens=%r total_tokens=%r reasoning_tokens=%r "
                "response_fields=%s choice_fields=%s message_fields=%s",
                model,
                finish_reason,
                len(choices),
                type(content).__name__,
                len(content) if isinstance(content, str) else 0,
                bool(getattr(message, "refusal", None)),
                len(getattr(message, "tool_calls", None) or []),
                getattr(usage, "prompt_tokens", None),
                getattr(usage, "completion_tokens", None),
                getattr(usage, "total_tokens", None),
                getattr(completion_details, "reasoning_tokens", None),
                response_fields,
                choice_fields,
                message_fields,
            )
            raise AppError("The model returned an empty response.", "empty_model_response", 502)
        return AITextResponse(text=content, usage=self._usage(response))

    async def analyze_image(
        self, prompt: str, image_data_url: str, *, max_tokens: int = 900
    ) -> AITextResponse:
        missing = self.settings.azure_missing_values(feature="vision")
        if missing:
            raise ConfigurationError(
                "Azure OpenAI vision is not configured.",
                f"Set the following environment variables: {', '.join(missing)}",
            )
        messages: list[dict[str, object]] = [
            {
                "role": "system",
                "content": (
                    "You analyze IT support screenshots. State what is visibly supported, distinguish "
                    "observations from hypotheses, never claim certainty you do not have, redact apparent "
                    "secrets, and recommend safe troubleshooting and escalation steps."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url, "detail": "high"}},
                ],
            },
        ]
        return await self.chat(
            messages,
            deployment=self.settings.azure_openai_vision_deployment,
            max_tokens=max_tokens,
            temperature=0.1,
        )

    async def close(self) -> None:
        await self.client.close()
        if self._credential:
            await self._credential.close()
