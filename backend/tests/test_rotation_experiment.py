import pytest
from app.rotation_experiment import predict_rotation

def sample():
    rows=[]
    for game in range(2):
        for pid in range(1,11):
            minutes=30 if pid<=5 else 18
            if pid==10:
                minutes=0.5
            rows.append({"season":2026,"game_id":game,"date_order":game,
                "player_id":pid,"minutes":minutes,"pts":minutes*.6,
                "reb":minutes*.2,"ast":minutes*.1,"fg3m":minutes*.03,
                "is_starter":pid<=5})
    return rows

def test_240_and_pra():
    result=predict_rotation(sample(),range(1,11),range(1,6),season=2026)
    assert result["allocated_minutes"]==pytest.approx(240)
    t=result["team_totals"]
    assert t["pra"]==pytest.approx(t["pts"]+t["reb"]+t["ast"])

def test_out_fixed_and_smoothed():
    result=predict_rotation(sample(),range(1,11),range(1,5),season=2026,
                            out_ids=[5],fixed_minutes={10:25})
    assert 5 not in result["players"]
    assert result["players"][10]["smoothed"] is True
    assert result["players"][10]["pts"]>0
    assert result["players"][10]["minutes"]==25
    assert result["allocated_minutes"]==pytest.approx(240)

def test_reject_prior_season():
    rows=sample()
    rows[0]["season"]=2025
    with pytest.raises(ValueError,match="outside selected season"):
        predict_rotation(rows,range(1,11),season=2026)

def test_small_out_cannot_trigger_replacement():
    with pytest.raises(ValueError,match=">=10"):
        predict_rotation(sample(),range(1,11),season=2026,
                         out_ids=[10],fixed_minutes={9:20})

def test_two_replacements_max():
    with pytest.raises(ValueError,match="At most two"):
        predict_rotation(sample(),range(1,11),season=2026,
                         out_ids=[1],fixed_minutes={7:20,8:20,9:20})

def test_small_out_keeps_other_minutes():
    before=predict_rotation(sample(),range(1,11),season=2026)
    after=predict_rotation(sample(),range(1,11),season=2026,out_ids=[10])
    for pid in range(1,10):
        assert after["minutes"][pid]==pytest.approx(before["minutes"][pid])
    assert after["partial"] is True
