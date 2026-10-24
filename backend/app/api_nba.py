"""Shared PostgreSQL-backed API-NBA quota and request pacing."""
import asyncio
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import Settings


class DailyBudgetExceeded(RuntimeError):
    pass


class APINBAError(RuntimeError):
    pass


class APINBAClient:
    LOCK_ID = 7202601

    def __init__(self, settings: Settings):
        self.settings = settings

    async def get(self, db: Session, endpoint: str, **params: Any) -> dict:
        if endpoint not in ("/games", "/players/statistics", "/seasons"):
            raise ValueError("Endpoint not permitted")
        if endpoint == "/players/statistics" and not params.get("game"):
            raise ValueError("game is required")
        if endpoint == "/games" and not (params.get("date") or (params.get("league") and params.get("season") is not None)):
            raise ValueError("games requires date or league+season")
        if not self.settings.api_nba_key:
            raise ValueError("API_NBA_KEY is missing")

        # The advisory lock is transaction-scoped and held through the HTTP
        # request. No commit until the response (or error) is received.
        # Use a dedicated DB session for API calls, not a request session with
        # unrelated uncommitted writes.
        try:
            db.execute(text("SELECT pg_advisory_xact_lock(:id)"), {"id": self.LOCK_ID})
            now = datetime.now(timezone.utc)
            day = now.date()
            db.execute(text("""
                INSERT INTO api_call_budget(utc_date,calls_used)
                VALUES (:day,0) ON CONFLICT(utc_date) DO NOTHING
            """), {"day": day})
            row = db.execute(text("""
                SELECT calls_used,last_call_at FROM api_call_budget
                WHERE utc_date=:day FOR UPDATE
            """), {"day": day}).one()
            if row.calls_used >= 90:
                raise DailyBudgetExceeded("90 API calls reached for UTC day")
            if row.last_call_at is not None:
                delay = 7 - (now - row.last_call_at).total_seconds()
                if delay > 0:
                    await asyncio.sleep(delay)
            # Reserve attempt before sending. Do not rollback reservation on
            # HTTP errors: a failed network attempt may still count upstream.
            timestamp = datetime.now(timezone.utc)
            db.execute(text("""
                UPDATE api_call_budget SET calls_used=calls_used+1,
                    last_call_at=:ts WHERE utc_date=:day
            """), {"ts": timestamp, "day": day})
            async with httpx.AsyncClient(timeout=20) as client:
                try:
                    response = await client.get(
                        self.settings.api_nba_base_url.rstrip("/") + endpoint,
                        params=params,
                        headers={"x-apisports-key": self.settings.api_nba_key},
                    )
                    response.raise_for_status()
                    data = response.json()
                except Exception:
                    db.commit()
                    raise
            db.commit()
            if not isinstance(data, dict):
                raise APINBAError("Unexpected API response")
            if data.get("errors"):
                raise APINBAError("Provider returned an API error")
            return data
        except Exception:
            db.rollback()
            raise
