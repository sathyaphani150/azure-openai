from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import openai
import pytest

from helpdesk.clients.azure_openai import AzureOpenAIProvider
from helpdesk.config import Settings
from helpdesk.errors import AppError


def _settings(auth_mode: str) -> Settings:
    return Settings(
        ai_provider="azure",
        azure_openai_endpoint="https://resource.invalid",
        azure_openai_api_version="test-api-version",
        azure_openai_auth_mode=auth_mode,
        azure_openai_api_key="test-secret" if auth_mode == "api_key" else None,
        azure_openai_chat_deployment="chat-deployment",
        azure_openai_embedding_deployment="embedding-deployment",
        azure_openai_vision_deployment="vision-deployment",
        _env_file=None,
    )


@patch("helpdesk.clients.azure_openai.AsyncOpenAI")
def test_api_key_authentication_is_passed_to_sdk(mock_client: MagicMock) -> None:
    """API-key mode uses the Foundry OpenAI-compatible v1 base URL."""
    AzureOpenAIProvider(_settings("api_key"))
    kwargs = mock_client.call_args.kwargs
    assert kwargs["api_key"] == "test-secret"
    assert kwargs["base_url"] == "https://resource.invalid/openai/v1/"
    assert "api_version" not in kwargs


@patch("helpdesk.clients.azure_openai.AsyncOpenAI")
@patch("helpdesk.clients.azure_openai.get_bearer_token_provider")
@patch("helpdesk.clients.azure_openai.DefaultAzureCredential")
def test_entra_authentication_uses_renewable_token_provider(
    mock_credential: MagicMock,
    mock_token_provider: MagicMock,
    mock_client: MagicMock,
) -> None:
    """Entra mode configures the documented Cognitive Services token scope."""
    provider_callable = MagicMock()
    mock_token_provider.return_value = provider_callable
    AzureOpenAIProvider(_settings("entra_id"))
    mock_token_provider.assert_called_once_with(
        mock_credential.return_value, "https://ai.azure.com/.default"
    )
    assert mock_client.call_args.kwargs["api_key"] is provider_callable


@patch("helpdesk.clients.azure_openai.AsyncOpenAI")
@patch("helpdesk.clients.azure_openai.get_bearer_token_provider")
@patch("helpdesk.clients.azure_openai.ClientSecretCredential")
def test_entra_service_principal_values_from_settings(
    mock_credential: MagicMock,
    mock_token_provider: MagicMock,
    mock_client: MagicMock,
) -> None:
    """A complete service-principal configuration uses `ClientSecretCredential`."""
    settings = _settings("entra_id").model_copy(
        update={
            "azure_tenant_id": "tenant",
            "azure_client_id": "client",
            "azure_client_secret": _settings("api_key").azure_openai_api_key,
        }
    )
    AzureOpenAIProvider(settings)
    mock_credential.assert_called_once_with(
        tenant_id="tenant", client_id="client", client_secret="test-secret"
    )
    assert mock_client.call_args.kwargs["api_key"] is mock_token_provider.return_value


@pytest.mark.asyncio
@patch("helpdesk.clients.azure_openai.AsyncOpenAI")
async def test_gpt5_chat_reserves_reasoning_and_visible_output_tokens(
    mock_client: MagicMock,
) -> None:
    """GPT-5 chat uses a safe minimum budget and low reasoning without sampling options."""
    sdk = mock_client.return_value
    sdk.chat.completions.create = AsyncMock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    finish_reason="stop",
                    message=SimpleNamespace(content="Grounded answer"),
                )
            ],
            usage=None,
        )
    )
    provider = AzureOpenAIProvider(_settings("api_key"))

    response = await provider.chat([{"role": "user", "content": "Issue"}], max_tokens=900)

    kwargs = sdk.chat.completions.create.await_args.kwargs
    assert response.text == "Grounded answer"
    assert kwargs["model"] == "chat-deployment"
    assert kwargs["max_completion_tokens"] == 1500
    assert kwargs["reasoning_effort"] == "low"
    assert "max_tokens" not in kwargs
    assert "temperature" not in kwargs
    assert "top_p" not in kwargs


@pytest.mark.asyncio
@patch("helpdesk.clients.azure_openai.AsyncOpenAI")
async def test_empty_chat_logs_safe_completion_diagnostics(
    mock_client: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """An exhausted reasoning budget logs structure and token counts, never request text."""
    message = SimpleNamespace(
        content="",
        refusal=None,
        tool_calls=None,
        model_fields_set={"role", "content", "refusal"},
    )
    choice = SimpleNamespace(
        finish_reason="length",
        message=message,
        model_fields_set={"finish_reason", "message"},
    )
    details = SimpleNamespace(reasoning_tokens=1500)
    usage = SimpleNamespace(
        prompt_tokens=1200,
        completion_tokens=1500,
        total_tokens=2700,
        completion_tokens_details=details,
    )
    sdk = mock_client.return_value
    sdk.chat.completions.create = AsyncMock(
        return_value=SimpleNamespace(
            choices=[choice],
            usage=usage,
            model_fields_set={"choices", "usage"},
        )
    )
    provider = AzureOpenAIProvider(_settings("api_key"))

    with caplog.at_level("WARNING"), pytest.raises(AppError) as exc_info:
        await provider.chat([{"role": "user", "content": "PRIVATE TEST PROMPT"}])

    assert exc_info.value.code == "empty_model_response"
    assert "model='chat-deployment'" in caplog.text
    assert "finish_reason='length'" in caplog.text
    assert "total_tokens=2700" in caplog.text
    assert "reasoning_tokens=1500" in caplog.text
    assert "PRIVATE TEST PROMPT" not in caplog.text


def test_quota_error_has_friendly_non_retryable_mapping() -> None:
    """Quota-flavoured 429 responses are distinct from temporary rate limiting."""
    request = httpx.Request("POST", "https://resource.invalid/openai/deployments/test")
    response = httpx.Response(429, request=request)
    source = openai.RateLimitError("Quota exceeded", response=response, body=None)
    mapped = AzureOpenAIProvider._map_error(source)
    assert mapped.code == "azure_quota_exceeded"
    assert mapped.retryable is False


@pytest.mark.asyncio
@patch("helpdesk.clients.azure_openai.AsyncOpenAI")
async def test_azure_web_search_invokes_responses_api(mock_client: MagicMock) -> None:
    """web_search invokes Responses API with built-in web_search tool and parses annotations."""
    annotation = SimpleNamespace(
        type="url_citation",
        url="https://example.com/docs",
        title="Example Docs",
    )
    content_block = SimpleNamespace(type="output_text", annotations=[annotation])
    message_item = SimpleNamespace(type="message", content=[content_block])
    fake_response = SimpleNamespace(
        output_text="Web search synthesized result.",
        output=[message_item],
        usage=SimpleNamespace(prompt_tokens=20, completion_tokens=30, total_tokens=50),
    )
    sdk = mock_client.return_value
    sdk.responses.create = AsyncMock(return_value=fake_response)

    provider = AzureOpenAIProvider(_settings("api_key"))
    res = await provider.web_search("search query")

    kwargs = sdk.responses.create.await_args.kwargs
    assert kwargs["model"] == "chat-deployment"
    assert kwargs["tools"] == [{"type": "web_search"}]
    assert kwargs["input"] == "search query"
    assert res.text == "Web search synthesized result."
    assert res.sources[0].source == "Web Search: Example Docs"
    assert res.sources[0].excerpt == "URL: https://example.com/docs"

