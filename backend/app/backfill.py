"""Resumable newest-first NBA backfill. No calls are made on import.

Requires schema.sql and 002_ingestion.sql. API-NBA response mappings must
be validated against an actual provider sample before enabling execution.
"""
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.orm import Session
from .api_nba import APINBAClient
from .ingestion import claim_game, complete_game, fail_game

def season_games(payload: dict) -> list[dict]:
    if not isinstance(payload.get("response"), list):
        raise ValueError("Missing games response list")
    return payload["response"]

def finished_game(raw: dict) -> bool:
    status = raw.get("status") or {}
    short = str(status.get("short", "")).upper()
    long = str(status.get("long", "")).lower()
    return short in {"FT", "AOT", "FINAL"} or long in {"finished", "final", "after overtime"}

def game_timestamp(raw: dict) -> datetime:
    value = raw.get("date")
    if not isinstance(value, str):
        raise ValueError("Missing game date")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

def ordered_finished_games(payload: dict) -> list[dict]:
    return sorted(
        (g for g in season_games(payload) if finished_game(g)),
        key=game_timestamp,
        reverse=True,
    )

def import_schedule(db: Session, payload: dict, season: int) -> int:
    """Persist schedule only; no box-score calls."""
    inserted = 0
    for raw in season_games(payload):
        home, away = raw.get("teams", {}).get("home"), raw.get("teams", {}).get("visitors")
        if not home or not away:
            raise ValueError("Game missing teams")
        for team in (home, away):
            db.execute(text("""
                INSERT INTO teams(api_id,code,name)
                VALUES (:api_id,:code,:name)
                ON CONFLICT(api_id) DO UPDATE SET code=EXCLUDED.code,name=EXCLUDED.name
            """), {"api_id": int(team["id"]), "code": team.get("code"), "name": team["name"]})
        result = db.execute(text("""
            INSERT INTO games(api_id,date_utc,season,home_team_id,away_team_id,
                              home_pts,away_pts,status)
            VALUES (:api_id,:date,:season,
              (SELECT id FROM teams WHERE api_id=:home),
              (SELECT id FROM teams WHERE api_id=:away),
              :home_pts,:away_pts,:status)
            ON CONFLICT(api_id) DO UPDATE SET
              date_utc=EXCLUDED.date_utc,status=EXCLUDED.status,
              home_pts=EXCLUDED.home_pts,away_pts=EXCLUDED.away_pts
            RETURNING id
        """), {
            "api_id": int(raw["id"]), "date": game_timestamp(raw),
            "season": season, "home": int(home["id"]), "away": int(away["id"]),
            "home_pts": (raw.get("scores", {}).get("home") or {}).get("points"),
            "away_pts": (raw.get("scores", {}).get("visitors") or {}).get("points"),
            "status": str((raw.get("status") or {}).get("long") or "unknown"),
        })
        result.scalar_one()
        inserted += 1
    db.commit()
    return inserted

def pending_finished_games(db: Session, season: int, limit: int = 100) -> list[tuple[int,int]]:
    return list(db.execute(text("""
        SELECT g.id,g.api_id FROM games g
        LEFT JOIN ingestion_state i ON i.game_id=g.id
        WHERE g.season=:season
          AND lower(g.status) IN ('finished','final','after overtime')
          AND (i.game_id IS NULL OR i.status IN ('pending','failed')
               OR (i.status='claimed' AND i.claimed_until < now()))
        ORDER BY g.date_utc DESC LIMIT :limit
    """), {"season": season, "limit": limit}).all())

async def fetch_one_box_score(db: Session, client: APINBAClient, game_id: int, api_id: int) -> dict | None:
    """One HTTP request per claimed game. No player-by-player requests.

    Returns raw payload for validation/import by the ingestion adapter.
    A claim is not marked complete until the adapter commits all player rows.
    """
    if not claim_game(db, game_id):
        return None
    try:
        payload = await client.get(db, "/players/statistics", game=api_id)
        if not isinstance(payload.get("response"), list) or not payload["response"]:
            raise ValueError("Empty or invalid player box score")
        return payload
    except Exception as exc:
        fail_game(db, game_id, str(exc))
        raise
