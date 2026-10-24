import pytest
from app.api_nba import APINBAClient

def test_rejects_unsupported_endpoint():
    client = APINBAClient(type("Settings", (), {"api_nba_key": "test"})())
    with pytest.raises(ValueError, match="Endpoint not permitted"):
        import asyncio
        asyncio.run(client.get(None, "/unknown"))

def test_requires_game_id():
    client = APINBAClient(type("Settings", (), {"api_nba_key": "test"})())
    with pytest.raises(ValueError, match="game is required"):
        import asyncio
        asyncio.run(client.get(None, "/players/statistics"))
