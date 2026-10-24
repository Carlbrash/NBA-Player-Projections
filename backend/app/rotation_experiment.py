"""Opt-in current-season rotation model. Does not modify baseline projections."""
from collections import defaultdict
from math import isfinite

STATS = ("pts", "reb", "ast", "fg3m")
TEAM_MINUTES = 240.0
MIN_SAMPLE = 5.0
OUT_THRESHOLD = 10.0

def _weighted(values):
    if not values:
        return 0.0
    weights = [0.5 ** ((len(values)-1-i)/10) for i in range(len(values))]
    return sum(v*w for v,w in zip(values, weights))/sum(weights)

def _allocate(weights, fixed=None):
    fixed = fixed or {}
    if any(not isfinite(v) or v < 0 or v > 48 for v in fixed.values()):
        raise ValueError("Fixed minutes must be between 0 and 48")
    remaining = TEAM_MINUTES-sum(fixed.values())
    if remaining < -1e-7:
        raise ValueError("Fixed minutes exceed team total")
    output = dict(fixed)
    pool = {k:max(0.0,v) for k,v in weights.items() if k not in fixed}
    while pool and remaining > 1e-9:
        denom = sum(pool.values())
        if denom <= 0:
            break
        capped = [k for k,v in pool.items() if remaining*v/denom >= 48]
        if not capped:
            output.update({k:remaining*v/denom for k,v in pool.items()})
            remaining = 0
            break
        for k in capped:
            output[k] = 48.0
            remaining -= 48.0
            del pool[k]
    for k in pool:
        output.setdefault(k,0.0)
    return output, remaining

def predict_rotation(history, available_ids, confirmed_starter_ids=None, season=None,
                     out_ids=None, fixed_minutes=None, position_by_player=None):
    """history: current-season pre-tipoff dict rows including game_id,
    date_order, player_id, minutes, pts, reb, ast, fg3m, is_starter.
    fixed_minutes is NEW TOTAL minutes for up to two bench players.
    """
    if season is None:
        raise ValueError("Current season is required")
    history = list(history)
    if any(r.get("season") != season for r in history):
        raise ValueError("Input contains games outside selected season")
    if any(r.get("minutes") is not None and
           (not isfinite(float(r["minutes"])) or float(r["minutes"]) < 0)
           for r in history):
        raise ValueError("Invalid minutes")
    all_available = set(available_ids)
    out = set(out_ids or ())
    available = all_available-out
    starters = set(confirmed_starter_ids or ())
    fixed = {int(k):float(v) for k,v in (fixed_minutes or {}).items()}
    if len(fixed)>2:
        raise ValueError("At most two replacement players")
    if not set(fixed)<=available:
        raise ValueError("Replacement must be available")
    if set(fixed)&starters:
        raise ValueError("Existing starters cannot be replacements")
    grouped = defaultdict(list)
    for row in history:
        if row.get("minutes") is not None:
            grouped[row["player_id"]].append(row)
    for rows in grouped.values():
        rows.sort(key=lambda r:(r["date_order"],r["game_id"]))
    def aggregate(rows,stat):
        w=[0.5**((len(rows)-1-i)/10) for i in range(len(rows))]
        denom=sum(float(r["minutes"])*x for r,x in zip(rows,w))
        return sum(float(r.get(stat,0) or 0)*x for r,x in zip(rows,w))/denom if denom else 0.0
    rates={}
    for pid in available:
        rows=grouped.get(pid,[])
        if not rows:
            continue
        own_minutes=sum(float(r["minutes"]) for r in rows)
        peers=[other for other in available if other!=pid and grouped.get(other)
               and sum(float(x["minutes"]) for x in grouped[other])>=MIN_SAMPLE]
        if position_by_player and position_by_player.get(pid):
            same=[other for other in peers if position_by_player.get(other)==position_by_player[pid]]
            if same:
                peers=same
        peer_rows=[r for other in peers for r in grouped[other]]
        rates[pid]={}
        for stat in STATS:
            if own_minutes<MIN_SAMPLE and peer_rows:
                denom=sum(float(r["minutes"]) for r in peer_rows)
                rate=sum(float(r.get(stat,0) or 0) for r in peer_rows)/denom if denom else 0.0
            else:
                rate=aggregate(rows,stat)
            rates[pid][stat]=rate
    weights={}
    for pid in available:
        rows=grouped.get(pid,[])
        if not rows:
            continue
        selected=[r for r in rows if r.get("is_starter") is (pid in starters)]
        weights[pid]=_weighted([float(r["minutes"]) for r in (selected or rows)])
    material_out=[]
    for pid in out:
        played=[r for r in grouped.get(pid,[]) if float(r["minutes"])>0]
        avg=sum(float(r["minutes"]) for r in played)/len(played) if played else 0
        if avg>=OUT_THRESHOLD:
            material_out.append(pid)
    if fixed and not material_out:
        raise ValueError("Manual replacement requires OUT with >=10 avg MIN")
    if out and not material_out:
        baseline_weights=dict(weights)
        for pid in out&all_available:
            rows=grouped.get(pid,[])
            if rows:
                baseline_weights[pid]=_weighted([float(r["minutes"]) for r in rows])
        before,_=_allocate(baseline_weights)
        allocation={pid:mins for pid,mins in before.items() if pid not in out}
        gap=TEAM_MINUTES-sum(allocation.values())
    else:
        allocation,gap=_allocate(weights,fixed)
    players={}
    for pid,minutes in allocation.items():
        stats={s:minutes*rates.get(pid,{}).get(s,0.0) for s in STATS}
        stats["pra"]=stats["pts"]+stats["reb"]+stats["ast"]
        sample=sum(float(r["minutes"]) for r in grouped.get(pid,[]))
        players[pid]={"minutes":minutes,**stats,"sample_minutes":sample,"smoothed":sample<MIN_SAMPLE}
    totals={s:sum(row[s] for row in players.values()) for s in (*STATS,"pra")}
    return {"players":players,"minutes":allocation,"points":{pid:r["pts"] for pid,r in players.items()},
            "team_points":totals["pts"],"team_totals":totals,
            "allocated_minutes":sum(allocation.values()),"remaining_minutes":gap,
            "partial":gap>1e-6,"material_out":sorted(material_out),
            "sample_games":len({r["game_id"] for r in history})}
