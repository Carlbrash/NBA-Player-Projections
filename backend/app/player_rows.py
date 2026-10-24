"""Date-aware player rows from PostgreSQL; never query external NBA API."""
from datetime import datetime,timezone
from sqlalchemy import text
from sqlalchemy.orm import Session

def game_player_rows(db:Session,game_id:int)->dict:
    game=db.execute(text("""
      SELECT id,date_utc,status,home_team_id,away_team_id
      FROM games WHERE id=:id
    """),{"id":game_id}).mappings().first()
    if game is None:raise LookupError("Game not found")
    is_final=str(game["status"]).lower() in ("finished","final","after overtime","ft","aot")
    if is_final:
        rows=db.execute(text("""
          SELECT p.id AS player_id,pg.game_id,p.name,t.code AS team_code,
            pg.pts,pg.reb,pg.ast,pg.fg3m,
            (pg.pts+pg.reb+pg.ast) AS pra,
            pg.source,pg.min
          FROM player_games pg JOIN players p ON p.id=pg.player_id
          JOIN teams t ON t.id=pg.team_id
          WHERE pg.game_id=:id ORDER BY pg.pts DESC,p.name
        """),{"id":game_id}).mappings().all()
    else:
        rows=db.execute(text("""
          SELECT p.player_id,p.game_id,pl.name,t.code AS team_code,
            p.proj_pts AS pts,p.proj_reb AS reb,p.proj_ast AS ast,
            p.proj_fg3m AS fg3m,p.proj_pra AS pra,
            p.sd_pts,p.sd_reb,p.sd_ast,p.sd_fg3m,p.sd_pra
          FROM projections p JOIN players pl ON pl.id=p.player_id
          JOIN teams t ON t.id=pl.team_id
          WHERE p.game_id=:id ORDER BY p.proj_pts DESC,pl.name
        """),{"id":game_id}).mappings().all()
    return {"game_id":game_id,"mode":"final" if is_final else "pregame",
            "rows":[dict(r) for r in rows]}
