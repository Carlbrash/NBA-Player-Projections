"""Read-only app API. No API-NBA calls on page load."""
from datetime import date
from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import text
from .config import Settings
from .database import session_factory
from .queries import daily_games, player_history, calculate_player
from .projection_model import over_probability, fair_odds

app=FastAPI(title="NBA Player Projections")
@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/api/games")
def games(day: date = Query(default_factory=date.today)):
    with session_factory(Settings())() as db:
        return daily_games(db,day.isoformat())

@app.get("/api/players/{player_id}/history")
def history(player_id: int):
    with session_factory(Settings())() as db:
        return player_history(db,player_id)[-25:]

@app.get("/api/players/{player_id}/projection/{game_id}")
def projection(player_id:int,game_id:int):
    with session_factory(Settings())() as db:
        result=calculate_player(db,player_id,game_id)
        if result is None:
            raise HTTPException(404,"Minimum 10 previous games required")
        return result

@app.get("/api/players/{player_id}/over")
def over(player_id:int,game_id:int,stat:str,line:float):
    if stat not in ("pts","reb","ast","fg3m","pra"):
        raise HTTPException(400,"Invalid stat")
    with session_factory(Settings())() as db:
        p=calculate_player(db,player_id,game_id)
        if p is None:
            raise HTTPException(404,"Insufficient history")
        item=p[stat]
        probability=over_probability(line,item["projection"],item["sd"],stat=="fg3m")
        return {"probability":probability,"fair_odds":fair_odds(probability)}
