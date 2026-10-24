"""Operator commands; do not schedule until tests and API schema verification."""
import argparse,asyncio,json
from .config import Settings
from .database import session_factory
from .api_nba import APINBAClient
from .daily import daily_update
from .jobs import import_season_schedule_once,run_backfill

async def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("command",choices=["daily","schedule","backfill"])
    parser.add_argument("--season",type=int,default=2026)
    parser.add_argument("--max-games",type=int,default=60)
    args=parser.parse_args()
    settings=Settings()
    with session_factory(settings)() as db:
        client=APINBAClient(settings)
        if args.command=="daily":
            result=await daily_update(db,client)
        elif args.command=="schedule":
            result={"games":await import_season_schedule_once(db,client,args.season)}
        else:
            result=await run_backfill(db,client,args.season,args.max_games)
        print(json.dumps(result,default=str))
if __name__=="__main__":
    asyncio.run(main())
