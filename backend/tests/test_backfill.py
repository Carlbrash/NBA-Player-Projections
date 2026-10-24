from app.backfill import ordered_finished_games, finished_game

def test_newest_finished_first():
    def game(id, date, status):
        return {"id":id,"date":date,"status":{"long":status}}
    payload = {"response":[
        game(1,"2026-10-21T01:00:00Z","Finished"),
        game(2,"2026-10-23T01:00:00Z","Scheduled"),
        game(3,"2026-10-22T01:00:00Z","Finished")
    ]}
    assert [g["id"] for g in ordered_finished_games(payload)] == [3,1]

def test_live_not_finished():
    assert not finished_game({"status":{"long":"In Play","short":"Q3"}})
