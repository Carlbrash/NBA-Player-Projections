# Historical backfill policy

## Priority
1. 2026–27 season (API season parameter expected `2026`, verify against `GET /seasons` before requesting).
2. 2025–26 season (expected `2025`, likewise verify).

Within each season, process **finished games newest-first**. Never ingest scheduled or live games as final box scores.

## Budget
Global API-NBA cap: 90 calls per UTC day, minimum seven seconds between requests. Reserve a configurable daily budget for automatic updates before allocating calls to backfill. Initial proposed reserve: 20 calls/day; adjust after measuring actual daily demand. Stop safely when the remaining allocation is insufficient. A failed or timed-out network attempt counts as a call.

## Resume and correctness
Store each game and its ingestion state in PostgreSQL; retry failed or incomplete box scores, skip successfully imported games, and upsert players using provider IDs. Do not delete screenshot data until a valid API replacement is ready. Record calls, errors and progress in update_log.

## Release gate
**Do not run historical imports yet.** First fix the API client cross-worker rate-limit race, verify API response schemas, and pass PostgreSQL integration tests. No production deployment without explicit approval.
