"""Coverage push for src/automation/notifications.py (lines 113, 130)."""

import pytest


@pytest.mark.asyncio
async def test_generate_filtered_notification_missing_meta() -> None:
    from src.automation.notifications import generate_filtered_notification

    result = await generate_filtered_notification(lambda s: {}, "missing", "dev")
    assert result.profile.name == "Unknown"


@pytest.mark.asyncio
async def test_generate_filtered_notification_low_relevance() -> None:
    from src.automation.notifications import generate_filtered_notification

    meta = {
        "categories": [{"name": "C", "count": 1}],
    }
    result = await generate_filtered_notification(lambda s: meta, "r", "admin")
    assert result is not None
