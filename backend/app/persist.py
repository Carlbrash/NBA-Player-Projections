"""Atomic box-score persistence; never mark incomplete imports complete."""
import unicodedata
from sqlalchemy import text
from sqlalchemy.orm import Session
from .boxscore import normalize_box_score

def normalized_name(name: str) -> str:
    value = unicodedata.normalize("NFKD", name.lower())
    return "".join(c for c in value if not unicodedata.combining(c) and c != ".")

def save_box_score(db: Session, game_id: int, payload: dict) -> int:
    rows = normalize_box_score(payload)
    game = db.execute(text("""
      SELECT g.id, ht.api_id AS home_api, at.api_id AS away_api,
             g.home_team_id, g.away_team_id
      FROM games g JOIN teams ht ON ht.id=g.home_team_id
      JOIN teams at ON at.id=g.away_team_id WHERE g.id=:id
    """), {"id":game_id}).mappings().one()
    if set(r["api_team_id"] for r in rows) != {game["home_api"],game["away_api"]}:
        raise ValueError("Box score must contain both game teams")
    try:
        for row in rows:
            team_id = game["home_team_id"] if row["api_team_id"] == game["home_api"] else game["away_team_id"]
            opponent_id = game["away_team_id"] if team_id == game["home_team_id"] else game["home_team_id"]
            db.execute(text("""
              INSERT INTO players(api_id,name,name_normalized,team_id)
              VALUES (:api_id,:name,:norm,:team_id)
              ON CONFLICT(api_id) DO UPDATE SET name=EXCLUDED.name,
                name_normalized=EXCLUDED.name_normalized,team_id=EXCLUDED.team_id
            """), {"api_id":row["api_player_id"],"name":row["player_name"],
                    "norm":normalized_name(row["player_name"]),"team_id":team_id})
            db.execute(text("""
              INSERT INTO player_games(player_id,game_id,team_id,opp_team_id,home,
                min,pts,reb,ast,fg3m,fgm,fga,ftm,fta,stl,blk,tov,plus_minus,source)
              VALUES ((SELECT id FROM players WHERE api_id=:player_api),:game_id,
                :team_id,:opp_id,:home,:min,:pts,:reb,:ast,:fg3m,:fgm,:fga,
                :ftm,:fta,:stl,:blk,:tov,:plus_minus,'api')
              ON CONFLICT(player_id,game_id) DO UPDATE SET
                team_id=EXCLUDED.team_id,opp_team_id=EXCLUDED.opp_team_id,
                home=EXCLUDED.home,min=EXCLUDED.min,pts=EXCLUDED.pts,
                reb=EXCLUDED.reb,ast=EXCLUDED.ast,fg3m=EXCLUDED.fg3m,
                fgm=EXCLUDED.fgm,fga=EXCLUDED.fga,ftm=EXCLUDED.ftm,
                fta=EXCLUDED.fta,stl=EXCLUDED.stl,blk=EXCLUDED.blk,
                tov=EXCLUDED.tov,plus_minus=EXCLUDED.plus_minus,source='api'
            """), {**row,"player_api":row["api_player_id"],"game_id":game_id,
                    "team_id":team_id,"opp_id":opponent_id,
                    "home":team_id==game["home_team_id"]})
        db.execute(text("""
          UPDATE ingestion_state SET status='complete',completed_at=now(),
            claimed_until=NULL,last_error=NULL,updated_at=now()
          WHERE game_id=:id AND status='claimed'
        """), {"id":game_id})
        db.commit()
        return len(rows)
    except Exception:
        db.rollback()
        raise
