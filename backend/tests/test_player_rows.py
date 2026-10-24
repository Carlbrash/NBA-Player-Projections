from unittest.mock import MagicMock
import pytest
from app.player_rows import game_player_rows

def test_missing_game():
    db=MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value=None
    with pytest.raises(LookupError):
        game_player_rows(db,999)
