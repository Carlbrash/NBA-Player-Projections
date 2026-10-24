"""Resumable season ingestion. One schedule request and one box-score request per game.

Run only after provider response schema has been checked in staging.
"""
import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from .api_nba import APINBAClient, DailyBudgetExceeded
from .backfill import import_schedule, pending_finished_games
from .ingestion import claim_game, fail_game
from .persist import save_box_score

async def sync_season(db:Session,client:APINBAClient,season:int=2026,max_games:int=60,reserve:int=20)->dict:
    if season not in (2026,2025):
        raise ValueError("Only seasons 2026 and 2025 are supported")
    result={"season":season,"schedule_calls":0,"boxscore_calls":0,"games_completed":0,"rows_saved":0,"errors":[]}
    # A completed schedule marker prevents repeated season-wide requests.
    marker=db.execute(text("SELECT complete FROM schedule_fetch_state WHERE season=:s"),{"s":season}).scalar_one_or_none()
    if marker is not True:
        response=await client.get(db,"/games",league="standard",season=season)
        result["schedule_calls"]=1
        count=import_schedule(db,response,season)
        db.execute(text("""
          INSERT INTO schedule_fetch_state(season,games_count,complete)
          VALUES (:s,:n,true) ON CONFLICT(season) DO UPDATE
          SET games_count=EXCLUDED.games_count,complete=true,fetched_at=now()
        """),{"s":season,"n":count})
        db.commit()
    for game_id,api_id in pending_finished_games(db,season,max_games):
        remaining=db.execute(text("""
          SELECT 90-calls_used FROM api_call_budget
          WHERE utc_date=(now() AT TIME ZONE 'UTC')::date
        """)).scalar_one_or_none()
        if remaining is not None and remaining<=reserve:
            break
        if not claim_game(db,game_id):
            continue
        try:
            result["boxscore_calls"]+=1
            response=await client.get(db,"/players/statistics",game=api_id)
            count=save_box_score(db,game_id,response)
            result["games_completed"]+=1
            result["rows_saved"]+=count
        except DailyBudgetExceeded:
            fail_game(db,game_id,"API daily safety cap")
            break
        except Exception as exc:
            fail_game(db,game_id,str(exc))
            result["errors"].append({"game_id":game_id,"reason":str(exc)})
    db.execute(text("""
      INSERT INTO update_log(type,calls_used,games_added,rows_added,errors)
      VALUES ('backfill',:calls,:games,:rows,CAST(:errors AS jsonb))
    """),{"calls":result["schedule_calls"]+result["boxscore_calls"],
          "games":result["games_completed"],"rows":result["rows_saved"],
          "errors":json.dumps(result["errors"])})
    db.commit()
    return result
