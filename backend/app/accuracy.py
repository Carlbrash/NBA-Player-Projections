"""Compare saved pregame snapshots against actual outcomes and pregame season means."""
from collections import defaultdict
from datetime import timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session

def weekly_accuracy(db:Session,days:int=56)->list[dict]:
    rows=db.execute(text("""
      SELECT p.player_id,g.date_utc,pg.pts,pg.reb,pg.ast,pg.fg3m,
        p.proj_pts,p.proj_reb,p.proj_ast,p.proj_fg3m,p.proj_pra,
        (SELECT avg(h.pts) FROM player_games h JOIN games gh ON gh.id=h.game_id
          WHERE h.player_id=p.player_id AND gh.date_utc<g.date_utc) AS base_pts,
        (SELECT avg(h.reb) FROM player_games h JOIN games gh ON gh.id=h.game_id
          WHERE h.player_id=p.player_id AND gh.date_utc<g.date_utc) AS base_reb,
        (SELECT avg(h.ast) FROM player_games h JOIN games gh ON gh.id=h.game_id
          WHERE h.player_id=p.player_id AND gh.date_utc<g.date_utc) AS base_ast,
        (SELECT avg(h.fg3m) FROM player_games h JOIN games gh ON gh.id=h.game_id
          WHERE h.player_id=p.player_id AND gh.date_utc<g.date_utc) AS base_fg3m
      FROM projections p JOIN games g ON g.id=p.game_id
      JOIN player_games pg ON pg.player_id=p.player_id AND pg.game_id=p.game_id
      WHERE g.date_utc>=now()-(:days * interval '1 day')
        AND p.created_at<g.date_utc
    """),{"days":days}).mappings()
    agg=defaultdict(lambda:{"n":0,"model":0.0,"baseline":0.0})
    for r in rows:
        week=r["date_utc"].date()-timedelta(days=r["date_utc"].weekday())
        for stat in ("pts","reb","ast","fg3m","pra"):
            actual=float(r["pts"]+r["reb"]+r["ast"]) if stat=="pra" else float(r[stat])
            base=(sum(float(r["base_"+s]) for s in ("pts","reb","ast"))
                  if stat=="pra" and all(r["base_"+s] is not None for s in ("pts","reb","ast"))
                  else r.get("base_"+stat))
            if base is None or r["proj_"+stat] is None:
                continue
            a=agg[(str(week),stat)]
            a["n"]+=1;a["model"]+=abs(actual-float(r["proj_"+stat]))
            a["baseline"]+=abs(actual-float(base))
    return [{"week":w,"stat":s,"n":a["n"],"model_mae":a["model"]/a["n"],
             "baseline_mae":a["baseline"]/a["n"]} for (w,s),a in sorted(agg.items())]
