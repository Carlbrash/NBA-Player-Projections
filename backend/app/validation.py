"""Validate one full box score before overwriting screenshot records."""
from .boxscore import normalize_box_score

def validated_game_rows(payload:dict,home_api_id:int,away_api_id:int)->list[dict]:
    rows=normalize_box_score(payload)
    teams={r["api_team_id"] for r in rows}
    if teams!={home_api_id,away_api_id}:
        raise ValueError("Incomplete box score: both teams required")
    if len(rows)<10:
        raise ValueError("Suspicious box score: fewer than 10 participating players")
    return rows
