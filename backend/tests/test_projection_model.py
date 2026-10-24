from app.projection_model import project, over_probability, fair_odds

def test_requires_ten_games():
    assert project([{"pts":10,"reb":5,"ast":2,"fg3m":1,"home":True}]*9, True) is None

def test_constant_player():
    games=[{"pts":20,"reb":5,"ast":4,"fg3m":2,"home":i%2==0} for i in range(12)]
    result=project(games, True)
    assert result["pts"]["projection"] == 20
    assert result["pra"]["projection"] == 29
    assert result["pts"]["sd"] == 0

def test_probabilities():
    assert abs(over_probability(20,20,5)-0.5)<1e-8
    assert fair_odds(0.5)==2
    assert 0<over_probability(1.5,2,1,True)<1
