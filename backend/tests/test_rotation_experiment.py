from app.rotation_experiment import predict_rotation

def history():
    rows=[]
    for game in range(12):
        for pid in range(1,11):
            starter=pid<=5
            minutes=32 if starter else 16
            rows.append({"season":2026,"game_id":game,"date_order":game,"player_id":pid,
                         "minutes":minutes,"pts":minutes*(0.8 if starter else 0.5),
                         "is_starter":starter})
    return rows

def test_team_minutes_exactly_240():
    r=predict_rotation(history(),range(1,11),range(1,6),season=2026)
    assert abs(sum(r["minutes"].values())-240)<1e-7
    assert r["team_points"] is not None

def test_absent_starter_redistributes_without_manual_weight():
    baseline=predict_rotation(history(),range(1,11),range(1,6),season=2026)
    out=predict_rotation(history(),range(2,11),range(2,7),season=2026)
    assert 1 not in out["minutes"]
    assert abs(sum(out["minutes"].values())-240)<1e-7
    assert out["minutes"][6] > baseline["minutes"][6]

def test_missing_rotation_cannot_invent_240_minutes():
    r=predict_rotation(history(),[1,2,3], [1,2,3],season=2026)
    assert r["team_points"] is None
    assert r["warning"]

def test_rejects_previous_season_data():
    from pytest import raises
    rows=history()
    rows[0]["season"]=2025
    with raises(ValueError,match="outside selected season"):
        predict_rotation(rows,range(1,11),season=2026)
