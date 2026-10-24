"""Read-only queries for frontend."""
from sqlalchemy import text
from sqlalchemy.orm import Session
from .projection_model import project, over_probability, fair_odds

def player_history(db: Session, player_id: int, before_game_id: int | None = None):
    sql = """
      SELECT pg.pts,pg.reb,pg.ast,pg.fg3m,pg.home,g.date_utc
      FROM player_games pg JOIN games g ON g.id=pg.game_id
      WHERE pg.player_id=:player_id
    """
    args={"player_id":player_id}
    if before_game_id is not None:
        sql += " AND g.date_utc < (SELECT date_utc FROM games WHERE id=:before)"
        args["before"]=before_game_id
    sql += " ORDER BY g.date_utc ASC, g.id ASC"
    return [dict(r) for r in db.execute(text(sql),args).mappings().all()]

def calculate_player(db: Session, player_id: int, game_id: int):
    game=db.execute(text("SELECT home_team_id,away_team_id FROM games WHERE id=:id"),{"id":game_id}).mappings().one()
    player=db.execute(text("SELECT team_id FROM players WHERE id=:id"),{"id":player_id}).mappings().one()
    home=player["team_id"]==game["home_team_id"]
    return project(player_history(db,player_id,game_id),home)

def daily_games(db: Session, date: str):
    return [dict(r) for r in db.execute(text("""
      SELECT g.id,g.api_id,g.date_utc,g.status,
        ht.name AS home_team,at.name AS away_team
      FROM games g JOIN teams ht ON ht.id=g.home_team_id
      JOIN teams at ON at.id=g.away_team_id
      WHERE (g.date_utc AT TIME ZONE 'UTC')::date=CAST(:date AS date)
      ORDER BY g.date_utc
    """),{"date":date}).mappings().all()]
