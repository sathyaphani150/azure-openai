from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class UsageInfo(BaseModel):
    """Token usage returned by an AI model when available."""

    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class SourceReference(BaseModel):
    """Knowledge-base evidence returned with a grounded response."""

    source: str
    page: int | None = None
    score: float
    excerpt: str


class QuestionRequest(BaseModel):
    """Validated employee helpdesk question."""

    question: str = Field(min_length=3, max_length=4000)


class AnswerResponse(BaseModel):
    """Grounded answer, evidence, usage, and request correlation data."""

    answer: str
    grounded: bool
    sources: list[SourceReference]
    usage: UsageInfo | None = None
    request_id: str


class GuideRequest(BaseModel):
    """Issue description used to generate a troubleshooting guide."""

    issue: str = Field(min_length=3, max_length=4000)


class GuideResponse(BaseModel):
    """Generated guide with grounding and usage metadata."""

    guide: str
    grounded: bool
    sources: list[SourceReference]
    usage: UsageInfo | None = None
    request_id: str


IssueCategory = Literal["VPN", "Wi-Fi", "Password", "Laptop", "Software", "Microsoft 365", "Other"]


class ClassificationRequest(BaseModel):
    """Issue description submitted for classification."""

    issue: str = Field(min_length=3, max_length=2000)


class ClassificationResult(BaseModel):
    """One category prediction with bounded confidence and rationale."""

    category: IssueCategory
    confidence: float = Field(ge=0, le=1)
    rationale: str


class ClassificationComparisonResponse(BaseModel):
    """Side-by-side zero-shot and few-shot classification output."""

    zero_shot: ClassificationResult
    few_shot: ClassificationResult
    same_category: bool
    usage: UsageInfo | None = None
    request_id: str


class RoleMessage(BaseModel):
    """One message in a role-based prompt demonstration."""

    role: Literal["system", "user", "assistant"]
    content: str


class RoleDemoRequest(BaseModel):
    """Follow-up question used in the role demonstration."""

    question: str = Field(min_length=3, max_length=2000)


class RoleDemoResponse(BaseModel):
    """Inspectable role messages and the generated assistant response."""

    messages: list[RoleMessage]
    response: str
    usage: UsageInfo | None = None
    request_id: str


class VisionResponse(BaseModel):
    """Screenshot analysis and non-sensitive request metadata."""

    analysis: str
    filename: str
    media_type: str
    usage: UsageInfo | None = None
    request_id: str


class ErrorBody(BaseModel):
    """Stable public error fields returned by the API."""

    code: str
    message: str
    retryable: bool = False
    request_id: str | None = None


class ErrorResponse(BaseModel):
    """Envelope for controlled API failures."""

    error: ErrorBody
