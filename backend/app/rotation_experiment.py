"""Experimental minutes-aware rotation model; baseline remains unchanged.

Input is CURRENT-SEASON player game appearances with is_starter from VERIFIED
game_starters only. Does not infer starters from box-score order.
"""
from collections import defaultdict
from math import exp

TEAM_MINUTES = 240.0

def weighted_mean(values, half_life=10):
    if not values:
        return None
    weights = [0.5 ** ((len(values) - 1 - i) / half_life) for i in range(len(values))]
    return sum(v*w for v,w in zip(values, weights)) / sum(weights)

def predict_rotation(history, available_ids, confirmed_starter_ids=None, season=None):
    """Return 240-minute allocation and team PTS estimate.

    history: iterable of CURRENT-SEASON dicts {season, game_id, player_id, minutes, pts,
      is_starter: bool, played: bool, date_order: int}.
    Missing is_starter must be None (unknown), never assumed False.
    Historical games sorted by date_order; most recent has greatest value.
    """
    if season is None:\n        raise ValueError("Current season is required; never mix prior seasons")\n    if any(row.get("season") != season for row in history):\n        raise ValueError("Input contains games outside selected season")\n    available_ids = set(available_ids)
    starters = set(confirmed_starter_ids or [])
    grouped = defaultdict(list)
    for row in history:
        if row.get("minutes") is None or row.get("pts") is None:
            continue
        grouped[row["player_id"]].append(row)
    predictions = []
    for player_id in sorted(available_ids):
        rows = sorted(grouped.get(player_id, []), key=lambda r:(r["date_order"],r["game_id"]))
        if not rows:
            continue
        # Include zero-minute DNP in minutes history only if explicitly recorded.
        minutes = weighted_mean([float(r["minutes"]) for r in rows])
        # Estimate player scoring rate from weighted aggregate points/minutes,
        # not the unstable average of individual game ratios.
        weights = [0.5 ** ((len(rows)-1-i)/10) for i in range(len(rows))]
        weighted_pts = sum(float(r["pts"])*w for r,w in zip(rows,weights))
        weighted_min = sum(float(r["minutes"])*w for r,w in zip(rows,weights))
        rate = weighted_pts / weighted_min if weighted_min > 0 else 0.0
        # Starter-conditioned minutes use verified starter appearances only.
        if player_id in starters:
            starts = [r for r in rows if r.get("is_starter") is True]
            if starts:
                minutes = weighted_mean([float(r["minutes"]) for r in starts])
        else:
            bench = [r for r in rows if r.get("is_starter") is False]
            if bench:
                minutes = weighted_mean([float(r["minutes"]) for r in bench])
        predictions.append({"player_id":player_id,"expected_minutes":max(0.0,minutes or 0.0),
                            "points_per_minute":rate})
    if not predictions:
        return {"minutes":{}, "points":{}, "team_points":None, "coverage":0,
                "sample_games":0, "partial":True}
    # Rescale rotation minutes to NBA regulation total; 0-48 minutes/player.
    # Iterative water filling prevents one player exceeding 48.
    remaining = TEAM_MINUTES
    active = list(predictions)
    allocation = {r["player_id"]:0.0 for r in predictions}
    while active and remaining > 1e-9:
        denom = sum(r["expected_minutes"] for r in active)
        if denom <= 0:
            break
        capped = [r for r in active if remaining*r["expected_minutes"]/denom >= 48]
        if not capped:
            for r in active:
                allocation[r["player_id"]] = remaining*r["expected_minutes"]/denom
            remaining = 0
            break
        for r in capped:
            allocation[r["player_id"]] = 48.0
            remaining -= 48.0
        active = [r for r in active if r not in capped]
    if remaining > 1e-6:
        # Show current-season evidence as-is; do not extrapolate a short
        # rotation to a fictitious 240-minute team total.
        observed = {r["player_id"]:r["expected_minutes"] for r in predictions}
        points = {r["player_id"]:observed[r["player_id"]]*r["points_per_minute"] for r in predictions}
        return {"minutes":observed,"points":points,"team_points":sum(points.values()),
                "coverage":len(predictions),"partial":True,
                "sample_games":len(set(r["game_id"] for r in history))}
    points = {r["player_id"]:allocation[r["player_id"]]*r["points_per_minute"] for r in predictions}
    return {"minutes":allocation,"points":points,
            "team_points":sum(points.values()),"coverage":len(predictions),
            "partial":False,"sample_games":len(set(r["game_id"] for r in history))}
