"""One-call-per-game incremental ingestion runner."""
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.orm import Session
from .api_nba import APINBAClient, DailyBudgetExceeded
from .backfill import import_schedule, pending_finished_games
from .ingestion import claim_game, fail_game
from .persist import save_box_score

async def run_backfill(db: Session, client: APINBAClient, season: int = 2026, max_games: int = 60) -> dict:
    """Schedule fetched once per season by caller; no redundant season calls."""
    result = {"season":season,"processed":0,"rows":0,"errors":[]}
    for game_id, api_id in pending_finished_games(db,season,max_games):
        if not claim_game(db,game_id):
            continue
        try:
            payload = await client.get(db,"/players/statistics",game=api_id)
            rows = save_box_score(db,game_id,payload)
            result["processed"] += 1
            result["rows"] += rows
        except DailyBudgetExceeded:
            fail_game(db,game_id,"Daily API budget exhausted")
            break
        except Exception as exc:
            fail_game(db,game_id,str(exc))
            result["errors"].append({"game_id":game_id,"error":str(exc)})
    db.execute(text("""
      INSERT INTO update_log(type,calls_used,games_added,rows_added,errors)
      VALUES ('backfill',:calls,:games,:rows,CAST(:errors AS jsonb))
    """),{"calls":result["processed"]+len(result["errors"]),
           "games":result["processed"],"rows":result["rows"],
           "errors":__import__("json").dumps(result["errors"])})
    db.commit()
    return result

async def import_season_schedule_once(db: Session, client: APINBAClient, season: int=2026) -> int:
    existing = db.execute(text("SELECT count(*) FROM games WHERE season=:s"),{"s":season}).scalar_one()
    if existing:
        return 0
    payload = await client.get(db,"/games",league="standard",season=season)
    return import_schedule(db,payload,season)
