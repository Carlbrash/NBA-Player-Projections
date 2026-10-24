from unittest.mock import AsyncMock,MagicMock
import pytest
from app.season_sync import sync_season

@pytest.mark.asyncio
async def test_unsupported_season_does_not_call_api():
    client=MagicMock()
    client.get=AsyncMock()
    with pytest.raises(ValueError):
        await sync_season(MagicMock(),client,2024)
    client.get.assert_not_awaited()
