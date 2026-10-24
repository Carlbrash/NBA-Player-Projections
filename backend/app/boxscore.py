"""Pure API-NBA box-score validation and normalization.

No network requests. Upstream response schema should be verified using a
sanitized sample before production imports.
"""
from decimal import Decimal

STAT_FIELDS = ("points", "totReb", "assists", "tpm", "fgm", "fga",
               "ftm", "fta", "steals", "blocks", "turnovers", "plusMinus")

def parse_minutes(value):
    if value in (None, "", "0", "00:00"):
        return None
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    value = str(value)
    if ":" in value:
        m, s = value.split(":", 1)
        return Decimal(m) + Decimal(s) / Decimal(60)
    return Decimal(value)

def normalize_player_row(raw: dict) -> dict | None:
    player = raw.get("player") or {}
    team = raw.get("team") or {}
    if not player.get("id") or not team.get("id"):
        raise ValueError("Player or team ID missing")
    minutes = parse_minutes(raw.get("min"))
    if minutes is None or minutes <= 0:
        return None
    for field in STAT_FIELDS:
        if raw.get(field) is None:
            raise ValueError(f"Missing {field} for player {player['id']}")
    pts = int(raw["points"])
    fgm = int(raw["fgm"])
    tpm = int(raw["tpm"])
    ftm = int(raw["ftm"])
    if pts != 2 * fgm + tpm + ftm:
        raise ValueError(f"Points mismatch for player {player['id']}")
    return {
        "api_player_id": int(player["id"]),
        "player_name": player.get("name") or f"{player.get('firstname','')} {player.get('lastname','')}".strip(),
        "api_team_id": int(team["id"]),
        "min": minutes,
        "pts": pts,
        "reb": int(raw["totReb"]),
        "ast": int(raw["assists"]),
        "fg3m": tpm,
        "fgm": fgm,
        "fga": int(raw["fga"]),
        "ftm": ftm,
        "fta": int(raw["fta"]),
        "stl": int(raw["steals"]),
        "blk": int(raw["blocks"]),
        "tov": int(raw["turnovers"]),
        "plus_minus": int(raw["plusMinus"]),
    }

def normalize_box_score(payload: dict) -> list[dict]:
    raw_rows = payload.get("response")
    if not isinstance(raw_rows, list) or not raw_rows:
        raise ValueError("Missing player statistics")
    rows = [parsed for raw in raw_rows if (parsed := normalize_player_row(raw)) is not None]
    if not rows:
        raise ValueError("No players with minutes")
    keys = [(r["api_player_id"], r["api_team_id"]) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate player/team rows")
    return rows
