"""Athens-time daily job logic. Invoke from an external scheduler at 08:00 and 10:00."""
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
from sqlalchemy import text
from sqlalchemy.orm import Session
from .api_nba import APINBAClient,DailyBudgetExceeded
from .backfill import import_schedule
from .jobs import run_backfill
from .snapshots import morning_snapshot

async def daily_update(db:Session,client:APINBAClient)->dict:
    today=datetime.now(ZoneInfo("Europe/Athens")).date()
    # Fetch UTC dates covering yesterday through tomorrow in Athens.
    utc_dates=sorted({(datetime.combine(today+timedelta(days=offset),
                  datetime.min.time(),ZoneInfo("Europe/Athens")).astimezone(timezone.utc)
                  +timedelta(hours=12)).date() for offset in (-1,0,1)})
    dates={str(d) for d in utc_dates}
    # Include adjacent UTC dates to cover NBA late-night US tipoffs.
    dates.update(str(d+timedelta(days=1)) for d in utc_dates)
    result={"dates":[],"imported":0,"snapshots":0,"errors":[]}
    for day in sorted(dates):
        try:
            payload=await client.get(db,"/games",date=day)
            import_schedule(db,payload,today.year if today.month>=9 else today.year-1)
            result["dates"].append(day)
        except DailyBudgetExceeded:
            result["errors"].append("Daily budget exhausted")
            return result
        except Exception as exc:
            result["errors"].append(str(exc))
    result["backfill"]=await run_backfill(db,client,today.year if today.month>=9 else today.year-1,max_games=20)
    upcoming=db.execute(text("""
       SELECT id FROM games WHERE date_utc>now() AND date_utc<now()+interval '48 hours'
    """)).scalars().all()
    for game_id in upcoming:
        result["snapshots"]+=morning_snapshot(db,game_id)
    return result
