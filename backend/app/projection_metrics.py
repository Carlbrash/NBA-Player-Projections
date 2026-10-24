"""Local-only last-five versus full-season form comparison."""
from statistics import mean

def form_comparison(history:list[dict])->dict:
    if not history:
        return {}
    stats=("pts","reb","ast","fg3m")
    result={}
    for stat in stats:
        values=[float(row[stat]) for row in history]
        season=mean(values)
        recent=mean(values[-5:])
        result[stat]={"last5":recent,"season":season,
                      "change_pct":((recent/season)-1)*100 if season else None}
    return result
