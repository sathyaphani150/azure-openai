import pytest

from helpdesk.clients.fakes import FakeAIProvider
from helpdesk.services.classification import ClassificationService


@pytest.mark.asyncio
async def test_zero_and_few_shot_use_same_taxonomy() -> None:
    result = await ClassificationService(FakeAIProvider()).compare(
        "Outlook will not synchronize my mailbox"
    )
    assert result.zero_shot.category == "Microsoft 365"
    assert result.few_shot.category == "Microsoft 365"
    assert result.same_category is True
    assert result.usage and result.usage.total_tokens
