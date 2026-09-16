from __future__ import annotations

import logging
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager

from helpdesk.schemas import UsageInfo

logger = logging.getLogger("helpdesk.usage")


def merge_usage(*items: UsageInfo | None) -> UsageInfo | None:
    """Combine usage records while preserving unavailable fields as `None`."""
    present = [item for item in items if item]
    if not present:
        return None

    def total(name: str) -> int | None:
        values = [getattr(item, name) for item in present]
        available = [value for value in values if value is not None]
        return sum(available) if available else None

    return UsageInfo(
        prompt_tokens=total("prompt_tokens"),
        completion_tokens=total("completion_tokens"),
        total_tokens=total("total_tokens"),
    )


def log_usage(*, feature: str, request_id: str, usage: UsageInfo | None, latency_ms: int) -> None:
    """Log non-sensitive token and latency telemetry for an AI operation."""
    logger.info(
        "ai_request_completed",
        extra={
            "feature": feature,
            "request_id": request_id,
            "latency_ms": latency_ms,
            "prompt_tokens": usage.prompt_tokens if usage else None,
            "completion_tokens": usage.completion_tokens if usage else None,
            "total_tokens": usage.total_tokens if usage else None,
        },
    )


@contextmanager
def elapsed_timer() -> Iterator[Callable[[], int]]:
    """Yield a callable that returns elapsed wall-clock milliseconds."""
    start = time.perf_counter()
    yield lambda: int((time.perf_counter() - start) * 1000)
