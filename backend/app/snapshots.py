"""Immutable pregame snapshots, never overwrite after tipoff."""
from datetime import datetime,timezone
from sqlalchemy import text
from sqlalchemy.orm import Session
from .queries import calculate_player

def save_pregame_projection(db:Session,player_id:int,game_id:int)->bool:
    game=db.execute(text("SELECT date_utc FROM games WHERE id=:id"),{"id":game_id}).scalar_one()
    if game<=datetime.now(timezone.utc):
        return False
    values=calculate_player(db,player_id,game_id)
    if values is None:
        return False
    fields=("pts","reb","ast","fg3m","pra")
    params={"player_id":player_id,"game_id":game_id}
    for stat in fields:
        params["proj_"+stat]=values[stat]["projection"]
        params["sd_"+stat]=values[stat]["sd"]
    cols=["player_id","game_id"]+["proj_"+s for s in fields]+["sd_"+s for s in fields]
    db.execute(text("INSERT INTO projections ("+",".join(cols)+") VALUES ("+
                    ",".join(":"+c for c in cols)+") ON CONFLICT(player_id,game_id) DO NOTHING"),params)
    db.commit()
    return True

def morning_snapshot(db:Session,game_id:int)->int:
    """Persist once; eligibility uses historical appearances for each player."""
    game=db.execute(text("SELECT home_team_id,away_team_id,date_utc FROM games WHERE id=:id"),{"id":game_id}).mappings().one()
    if game["date_utc"]<=datetime.now(timezone.utc):
        return 0
    players=db.execute(text("""
       SELECT p.id FROM players p WHERE p.team_id IN (:home,:away)
    """),{"home":game["home_team_id"],"away":game["away_team_id"]}).scalars().all()
    return sum(save_pregame_projection(db,pid,game_id) for pid in players)
