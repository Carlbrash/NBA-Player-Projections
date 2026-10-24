from app.screenshot import validate_rows

def test_points_mismatch_is_flagged():
    row={"pts":11,"fgm":4,"fg3m":2,"ftm":0,"reb":3,"ast":2,
         "fga":9,"fta":0,"tov":1,"stl":0,"blk":0}
    assert validate_rows([row])

def test_valid_player_row():
    row={"pts":10,"fgm":4,"fg3m":2,"ftm":0,"reb":3,"ast":2,
         "fga":9,"fta":0,"tov":1,"stl":0,"blk":0}
    assert validate_rows([row])==[]
