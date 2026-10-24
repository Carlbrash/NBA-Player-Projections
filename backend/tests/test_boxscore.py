import pytest
from app.boxscore import normalize_box_score

def row(points=10):
    return {"player":{"id":1,"name":"Sample Player"},"team":{"id":2},"min":"22:30",
      "points":points,"totReb":4,"assists":3,"tpm":2,"fgm":4,"fga":9,
      "ftm":0,"fta":0,"steals":1,"blocks":0,"turnovers":1,"plusMinus":2}

def test_valid_boxscore():
    assert normalize_box_score({"response":[row()]})[0]["pts"]==10

def test_points_mismatch_rejected():
    with pytest.raises(ValueError,match="Points mismatch"):
        normalize_box_score({"response":[row(11)]})

def test_duplicate_player_rejected():
    with pytest.raises(ValueError,match="Duplicate"):
        normalize_box_score({"response":[row(),row()]})
