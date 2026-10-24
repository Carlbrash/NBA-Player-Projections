"""DST-aware daily orchestration, invoked by external scheduler.

Do not enable until API response mapping and integration tests pass.
"""
import argparse
import asyncio
import json
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import text
from .api_nba import APINBAClient, DailyBudgetExceeded
from .config import Settings
from .database import session_factory
from .backfill import import_schedule
from .season_sync import sync_season
from .projection_batch import generate_upcoming

ATHENS = ZoneInfo("Europe/Athens")

def utc_schedule_dates(now: datetime) -> list[str]:
    local = now.astimezone(ATHENS)
    start = datetime.combine(local.date()-timedelta(days=1),datetime.min.time(),ATHENS).astimezone(timezone.utc).date()
    end = datetime.combine(local.date()+timedelta(days=2),datetime.min.time(),ATHENS).astimezone(timezone.utc).date()
    return [(start+timedelta(days=i)).isoformat() for i in range((end-start).days+1)]

async def run_daily(retry_only: bool=False) -> dict:
    settings=Settings()
    result={"mode":"retry" if retry_only else "daily","dates":[],"snapshots":0,"errors":[]}
    with session_factory(settings)() as db:
        client=APINBAClient(settings)
        local_now=datetime.now(ATHENS)
        season=local_now.year if local_now.month>=9 else local_now.year-1
        for day in utc_schedule_dates(datetime.now(timezone.utc)):
            # Persist date fetches; do not burn calls re-fetching a day in same UTC day.
            existing=db.execute(text("""
                SELECT completed_at FROM schedule_day_state
                WHERE schedule_date=CAST(:d AS date)
            """),{"d":day}).scalar_one_or_none()
            if existing is not None:
                continue
            try:
                payload=await client.get(db,"/games",date=day)
                count=import_schedule(db,payload,season)
                db.execute(text("""
                    INSERT INTO schedule_day_state(schedule_date,completed_at,games_count)
                    VALUES (CAST(:d AS date),now(),:n)
                    ON CONFLICT(schedule_date) DO UPDATE
                    SET completed_at=now(),games_count=EXCLUDED.games_count
                """),{"d":day,"n":count})
                db.commit()
                result["dates"].append(day)
            except DailyBudgetExceeded:
                result["errors"].append("Daily API cap reached")
                return result
            except Exception as exc:
                db.rollback()
                result["errors"].append(str(exc))
        # The 10:00 retry should focus on incomplete box scores, not the
        # season-wide backfill, which is reserved for a separate worker.
        from .jobs import run_backfill
        if retry_only:
            result["ingestion"]=await run_backfill(db,client,season,max_games=10)
        else:
            result["ingestion"]=await sync_season(db,client,season,max_games=20,reserve=20)
        result["snapshots"]=generate_upcoming(db,48)["eligible"]
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--retry-only",action="store_true")
    args=parser.parse_args()
    print(json.dumps(asyncio.run(run_daily(args.retry_only)),default=str))
