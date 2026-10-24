"""DST-aware job entry point. Intended for an external scheduler."""
import argparse
import asyncio
import json
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import text
from .api_nba import APINBAClient,DailyBudgetExceeded
from .config import Settings
from .database import session_factory
from .backfill import import_schedule
from .season_sync import sync_season
from .snapshots import morning_snapshot

ATHENS=ZoneInfo("Europe/Athens")

def utc_schedule_dates(now:datetime)->list[str]:
    """UTC dates needed to cover yesterday, today, tomorrow in Athens."""
    local=now.astimezone(ATHENS)
    start=(datetime.combine(local.date()-timedelta(days=1),datetime.min.time(),ATHENS)).astimezone(timezone.utc).date()
    end=(datetime.combine(local.date()+timedelta(days=2),datetime.min.time(),ATHENS)).astimezone(timezone.utc).date()
    return [(start+timedelta(days=i)).isoformat() for i in range((end-start).days+1)]

async def run_daily(retry_only:bool=False)->dict:
    settings=Settings()
    result={"mode":"retry" if retry_only else "daily","dates":[],"snapshots":0,"errors":[]}
    with session_factory(settings)() as db:
        client=APINBAClient(settings)
        season=datetime.now(ATHENS).year if datetime.now(ATHENS).month>=9 else datetime.now(ATHENS).year-1
        for day in utc_schedule_dates(datetime.now(timezone.utc)):
            # Retry job must not refetch dates that already have complete schedules.
            if retry_only:
                existing=db.execute(text("""
                    SELECT count(*) FROM games WHERE (date_utc AT TIME ZONE 'UTC')::date=CAST(:d AS date)
                """),{"d":day}).scalar_one()
                if existing:
                    continue
            try:
                payload=await client.get(db,"/games",date=day)
                import_schedule(db,payload,season)
                result["dates"].append(day)
            except DailyBudgetExceeded:
                result["errors"].append("Daily API cap reached")
                return result
            except Exception as exc:
                result["errors"].append(str(exc))
        sync=await sync_season(db,client,season,max_games=20,reserve=20)
        result["ingestion"]=sync
        upcoming=db.execute(text("""
            SELECT id FROM games WHERE date_utc>now()
              AND date_utc<now()+interval '48 hours'
        """)).scalars().all()
        for game_id in upcoming:
            try:
                result["snapshots"]+=morning_snapshot(db,game_id)
            except Exception as exc:
                result["errors"].append(f"snapshot {game_id}: {exc}")
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--retry-only",action="store_true")
    args=parser.parse_args()
    print(json.dumps(asyncio.run(run_daily(args.retry_only)),default=str))
