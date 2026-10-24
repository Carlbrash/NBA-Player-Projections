"""Pregame-only projection calculations; no network calls."""
from math import erf, exp, factorial, sqrt
from statistics import mean, stdev

STATS = ("pts", "reb", "ast", "fg3m", "pra")
K = {"pts": 200, "reb": 60, "ast": 50}

def project(history: list[dict], home: bool, opponent_factors: dict | None = None):
    """History must be oldest-to-newest and exclude current/future games."""
    if len(history) < 10:
        return None
    factors = opponent_factors or {}
    output = {}
    for stat in STATS:
        values = [float(g["pts"]+g["reb"]+g["ast"]) if stat=="pra" else float(g[stat]) for g in history]
        weights = [0.5**((len(values)-1-i)/10) for i in range(len(values))]
        form = sum(v*w for v,w in zip(values,weights))/sum(weights)
        overall = mean(values)
        venue_values = [v for v,g in zip(values,history) if bool(g["home"])==home]
        ratio = mean(venue_values)/overall if venue_values and overall>0 else 1
        venue_factor = 1+(ratio-1)*len(venue_values)/(len(venue_values)+40)
        opponent_factor = float(factors.get(stat,1)) if stat in K else 1
        projection = max(0,form*venue_factor*opponent_factor)
        recent = values[-30:]
        sd = stdev(recent) if len(recent)>1 else 0
        output[stat] = {"projection":projection,"sd":sd,
                        "lower80":max(0,projection-1.2816*sd),
                        "upper80":projection+1.2816*sd}
    return output

def over_probability(line: float, projection: float, sd: float, three_pointers: bool=False) -> float:
    if three_pointers:
        # Count strictly above the line; valid for integer-valued 3PM.
        from math import floor
        cutoff = max(-1, floor(line))
        return max(0.0,min(1.0,1-sum(exp(-projection)*projection**k/factorial(k) for k in range(cutoff+1))))
    if sd <= 0:
        return 1.0 if projection > line else 0.0
    z = (line-projection)/(sd*sqrt(2))
    return max(0.0,min(1.0,0.5*(1-erf(z))))

def fair_odds(probability: float):
    return 1/probability if probability>0 else None
