"""Persist immutable pregame projections for upcoming games, no external calls."""
from datetime import datetime,timezone
from sqlalchemy import text
from sqlalchemy.orm import Session
from .snapshots import save_pregame_projection

def generate_upcoming(db:Session,hours:int=48)->dict:
    if hours<1 or hours>168: raise ValueError("hours must be 1..168")
    games=db.execute(text("""
      SELECT id,home_team_id,away_team_id FROM games
      WHERE date_utc>now() AND date_utc<now()+(:hours * interval '1 hour')
      ORDER BY date_utc
    """),{"hours":hours}).mappings().all()
    attempted=saved=0
    for game in games:
        player_ids=db.execute(text("""
          SELECT id FROM players WHERE team_id IN (:home,:away)
        """),{"home":game["home_team_id"],"away":game["away_team_id"]}).scalars()
        for pid in player_ids:
            attempted+=1
            if save_pregame_projection(db,pid,game["id"]):
                saved+=1
    return {"games":len(games),"attempted":attempted,"eligible":saved}

def current_projection_count(db:Session)->int:
    return db.execute(text("""
      SELECT count(*) FROM projections p JOIN games g ON g.id=p.game_id
      WHERE g.date_utc>now()
    """)).scalar_one()
