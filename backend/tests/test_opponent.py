from app.projection_model import project

def test_no_opponent_factor_for_threes():
    games=[{"pts":20,"reb":5,"ast":3,"fg3m":2,"home":True} for _ in range(12)]
    result=project(games,True,{"pts":1.1,"reb":1.2,"ast":1.3,"fg3m":4})
    assert result["pts"]["projection"]>20
    assert result["fg3m"]["projection"]==2
