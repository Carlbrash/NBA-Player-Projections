"""Requires TEST_DATABASE_URL pointing to an isolated PostgreSQL test DB."""
import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.ingestion import claim_game, complete_game, fail_game

@pytest.fixture
def db():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not configured")
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.execute(text("INSERT INTO teams(api_id,name) VALUES (-101,'Test A'),(-102,'Test B') ON CONFLICT(api_id) DO NOTHING"))
        connection.execute(text("""
          INSERT INTO games(api_id,date_utc,season,home_team_id,away_team_id,status)
          SELECT -90001,now(),2026,
            (SELECT id FROM teams WHERE api_id=-101),
            (SELECT id FROM teams WHERE api_id=-102),'Finished'
          ON CONFLICT(api_id) DO NOTHING
        """))
        connection.execute(text("DELETE FROM ingestion_state WHERE game_id=(SELECT id FROM games WHERE api_id=-90001)"))
    try:
        with Session(engine) as session:
            game_id = session.execute(text("SELECT id FROM games WHERE api_id=-90001")).scalar_one()
            yield session, game_id
    finally:
        with engine.begin() as connection:
            connection.execute(text("DELETE FROM ingestion_state WHERE game_id=(SELECT id FROM games WHERE api_id=-90001)"))
            connection.execute(text("DELETE FROM games WHERE api_id=-90001"))
            connection.execute(text("DELETE FROM teams WHERE api_id IN (-101,-102)"))
        engine.dispose()

def test_completed_game_never_claimed_twice(db):
    session, game_id = db
    assert claim_game(session, game_id)
    assert not claim_game(session, game_id)
    complete_game(session, game_id)
    assert not claim_game(session, game_id)

def test_failed_game_can_retry(db):
    session, game_id = db
    assert claim_game(session, game_id)
    fail_game(session, game_id, "incomplete box score")
    assert claim_game(session, game_id)
