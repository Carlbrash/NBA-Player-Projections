"""Player projection API uses immutable snapshots when available."""
from datetime import date
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .config import Settings
from .database import session_factory
from .queries import daily_games, player_history, calculate_player
from .projection_model import over_probability, fair_odds
from .accuracy import weekly_accuracy

app=FastAPI(title="NBA Player Projections")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:3000"],
                   allow_credentials=False,allow_methods=["GET"],allow_headers=["*"])

def get_snapshot(db,player_id:int,game_id:int):
    return db.execute(text("""
      SELECT proj_pts,proj_reb,proj_ast,proj_fg3m,proj_pra,
             sd_pts,sd_reb,sd_ast,sd_fg3m,sd_pra
      FROM projections WHERE player_id=:p AND game_id=:g
      ORDER BY created_at ASC LIMIT 1
    """),{"p":player_id,"g":game_id}).mappings().first()

@app.get("/health")
def health(): return {"status":"ok"}

@app.get("/api/games")
def games(day:date=Query(default_factory=date.today)):
    with session_factory(Settings())() as db:
        return daily_games(db,day.isoformat())

@app.get("/api/players/{player_id}/history")
def history(player_id:int):
    with session_factory(Settings())() as db:
        return player_history(db,player_id)[-25:]

@app.get("/api/players/{player_id}/projection/{game_id}")
def projection(player_id:int,game_id:int):
    with session_factory(Settings())() as db:
        snapshot=get_snapshot(db,player_id,game_id)
        if snapshot:
            return {s:{"projection":float(snapshot["proj_"+s]),
                       "sd":float(snapshot["sd_"+s])}
                    for s in ("pts","reb","ast","fg3m","pra")}
        result=calculate_player(db,player_id,game_id)
        if result is None: raise HTTPException(404,"Minimum 10 previous games required")
        return result

@app.get("/api/players/{player_id}/over")
def over(player_id:int,game_id:int,stat:str,line:float):
    if stat not in ("pts","reb","ast","fg3m","pra"):
        raise HTTPException(400,"Invalid stat")
    with session_factory(Settings())() as db:
        snapshot=get_snapshot(db,player_id,game_id)
        if snapshot:
            p=float(snapshot["proj_"+stat]);sd=float(snapshot["sd_"+stat])
        else:
            result=calculate_player(db,player_id,game_id)
            if result is None: raise HTTPException(404,"Insufficient history")
            p=result[stat]["projection"];sd=result[stat]["sd"]
        probability=over_probability(line,p,sd,stat=="fg3m")
        return {"probability":probability,"fair_odds":fair_odds(probability)}

@app.get("/api/accuracy")
def accuracy():
    with session_factory(Settings())() as db:
        return weekly_accuracy(db)

@app.get("/api/projections")
def projections(day:date=Query(default_factory=date.today)):
    with session_factory(Settings())() as db:
        return [dict(r) for r in db.execute(text("""
          SELECT p.player_id,p.game_id,pl.name AS player_name,
            t.name AS team_name,g.date_utc,
            p.proj_pts,p.proj_reb,p.proj_ast,p.proj_fg3m,p.proj_pra,
            p.sd_pts,p.sd_reb,p.sd_ast,p.sd_fg3m,p.sd_pra
          FROM projections p JOIN players pl ON pl.id=p.player_id
          JOIN teams t ON t.id=pl.team_id JOIN games g ON g.id=p.game_id
          WHERE (g.date_utc AT TIME ZONE 'UTC')::date=CAST(:day AS date)
          ORDER BY g.date_utc,pl.name
        """),{"day":day.isoformat()}).mappings().all()]

from .screenshot import router as screenshot_router
app.include_router(screenshot_router)

@app.get("/api/status")
def status():
    from datetime import datetime,timezone
    today=datetime.now(timezone.utc).date()
    with session_factory(Settings())() as db:
        used=db.execute(text("SELECT calls_used FROM api_call_budget WHERE utc_date=:d"),{"d":today}).scalar_one_or_none() or 0
        return {"utc_date":str(today),"calls_used":used,"remaining":max(0,90-used)}

from .player_rows import game_player_rows

@app.get("/api/games/{game_id}/player-rows")
def player_rows_for_game(game_id:int):
    with session_factory(Settings())() as db:
        try:
            return game_player_rows(db,game_id)
        except LookupError:
            raise HTTPException(404,"Game not found")
