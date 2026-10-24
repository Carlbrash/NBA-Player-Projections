"""PostgreSQL integration test for atomic daily cap."""
import os
from concurrent.futures import ThreadPoolExecutor
import pytest
from sqlalchemy import create_engine, text

def test_budget_row_lock_serializes_reservations():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not configured")
    engine = create_engine(url)
    with engine.begin() as con:
        con.execute(text("DELETE FROM api_call_budget WHERE utc_date='2099-01-01'"))
        con.execute(text("INSERT INTO api_call_budget(utc_date,calls_used) VALUES ('2099-01-01',89)"))
    def reserve():
        with engine.begin() as con:
            row = con.execute(text("SELECT calls_used FROM api_call_budget WHERE utc_date='2099-01-01' FOR UPDATE")).scalar_one()
            if row >= 90:
                return False
            con.execute(text("UPDATE api_call_budget SET calls_used=calls_used+1 WHERE utc_date='2099-01-01'"))
            return True
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: reserve(), range(2)))
        assert sorted(results) == [False, True]
        with engine.connect() as con:
            assert con.execute(text("SELECT calls_used FROM api_call_budget WHERE utc_date='2099-01-01'")).scalar_one() == 90
    finally:
        with engine.begin() as con:
            con.execute(text("DELETE FROM api_call_budget WHERE utc_date='2099-01-01'"))
        engine.dispose()
