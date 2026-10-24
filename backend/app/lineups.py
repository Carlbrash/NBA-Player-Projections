"""Read verified starting five for the selected game; historical points from same game."""
from sqlalchemy import text
from sqlalchemy.orm import Session

def get_game_lineups(db:Session,game_id:int)->dict:
    game=db.execute(text("""
      SELECT g.id,g.status,g.home_team_id,g.away_team_id,
        ht.code AS home_code,ht.name AS home_name,
        at.code AS away_code,at.name AS away_name
      FROM games g JOIN teams ht ON ht.id=g.home_team_id
      JOIN teams at ON at.id=g.away_team_id WHERE g.id=:id
    """),{"id":game_id}).mappings().first()
    if game is None:raise LookupError("Game not found")
    final=str(game["status"]).lower() in ("finished","final","after overtime","ft","aot")
    rows=db.execute(text("""
      SELECT gs.team_id,gs.player_id,p.name,gs.position,gs.confirmed,gs.source,
             pg.pts AS actual_pts
      FROM game_starters gs JOIN players p ON p.id=gs.player_id
      LEFT JOIN player_games pg ON pg.game_id=gs.game_id AND pg.player_id=gs.player_id
      WHERE gs.game_id=:id ORDER BY gs.team_id,gs.recorded_at,gs.player_id
    """),{"id":game_id}).mappings().all()
    teams=[]
    for side in ("away","home"):
        team_id=game[side+"_team_id"]
        starters=[{"playerId":r["player_id"],"name":r["name"],
                   "position":r["position"],"actualPts":r["actual_pts"] if final else None,
                   "jerseyNumber":None,"photoUrl":None,"source":r["source"]}
                  for r in rows if r["team_id"]==team_id and r["confirmed"]]
        teams.append({"side":side,"code":game[side+"_code"],
                      "name":game[side+"_name"],"starters":starters})
    verified=all(len(t["starters"])==5 for t in teams)
    status="historical" if final and verified else ("confirmed" if verified else "unavailable")
    return {"game_id":game_id,"status":status,"teams":teams}
