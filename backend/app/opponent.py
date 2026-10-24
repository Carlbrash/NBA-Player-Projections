"""Leakage-free opponent defensive adjustment from stored historical games."""
from sqlalchemy import text
from sqlalchemy.orm import Session

K={"pts":200.0,"reb":60.0,"ast":50.0}
def factors(db:Session,opponent_team_id:int,cutoff,season:int)->dict:
    # Player expected production is calculated using their games strictly
    # before the game being assessed, never the same or future games.
    rows=db.execute(text("""
      SELECT pg.player_id,pg.pts,pg.reb,pg.ast,g.date_utc
      FROM player_games pg JOIN games g ON g.id=pg.game_id
      WHERE pg.opp_team_id=:opp AND g.season=:season
        AND g.date_utc<:cutoff ORDER BY g.date_utc,g.id
    """),{"opp":opponent_team_id,"season":season,"cutoff":cutoff}).mappings().all()
    actual={s:0.0 for s in K};expected={s:0.0 for s in K}
    for row in rows:
        averages=db.execute(text("""
          SELECT avg(pg.pts) AS pts,avg(pg.reb) AS reb,avg(pg.ast) AS ast
          FROM player_games pg JOIN games g ON g.id=pg.game_id
          WHERE pg.player_id=:player AND g.season=:season
            AND g.date_utc<:date
        """),{"player":row["player_id"],"season":season,"date":row["date_utc"]}).mappings().one()
        if any(averages[s] is None for s in K):
            continue
        for s in K:
            actual[s]+=float(row[s]);expected[s]+=float(averages[s])
    return {s:(actual[s]+K[s])/(expected[s]+K[s]) for s in K}
