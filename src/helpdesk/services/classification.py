from __future__ import annotations

import json
from uuid import uuid4

from pydantic import ValidationError as PydanticValidationError

from helpdesk.clients.protocols import AIProvider
from helpdesk.errors import AppError
from helpdesk.observability.usage import elapsed_timer, log_usage, merge_usage
from helpdesk.prompts.classification import CLASSIFIER_SYSTEM_PROMPT, FEW_SHOT_MESSAGES
from helpdesk.schemas import ClassificationComparisonResponse, ClassificationResult, UsageInfo


class ClassificationService:
    """Run and compare zero-shot and few-shot issue classification."""

    def __init__(self, provider: AIProvider):
        self.provider = provider

    async def _classify(
        self, issue: str, *, few_shot: bool
    ) -> tuple[ClassificationResult, UsageInfo | None]:
        messages: list[dict[str, object]] = [
            {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT}
        ]
        if few_shot:
            messages.extend(FEW_SHOT_MESSAGES)
        messages.append({"role": "user", "content": issue})
        response = await self.provider.chat(messages, response_format={"type": "json_object"})
        try:
            result = ClassificationResult.model_validate(json.loads(response.text))
        except (json.JSONDecodeError, PydanticValidationError) as exc:
            raise AppError(
                "The classification model returned an invalid structured response.",
                "invalid_model_response",
                502,
            ) from exc
        return result, response.usage

    async def compare(
        self, issue: str, request_id: str | None = None
    ) -> ClassificationComparisonResponse:
        """Return both classification approaches using one controlled taxonomy."""
        request_id = request_id or str(uuid4())
        with elapsed_timer() as elapsed:
            zero, zero_usage = await self._classify(issue, few_shot=False)
            few, few_usage = await self._classify(issue, few_shot=True)
            usage = merge_usage(zero_usage, few_usage)
            log_usage(
                feature="classification",
                request_id=request_id,
                usage=usage,
                latency_ms=elapsed(),
            )
            return ClassificationComparisonResponse(
                zero_shot=zero,
                few_shot=few,
                same_category=zero.category == few.category,
                usage=usage,
                request_id=request_id,
            )
