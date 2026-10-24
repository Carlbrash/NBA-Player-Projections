# Frank — deployment handoff / DO NOT SHIP UNTIL VERIFIED

Repository: Carlbrash/NBA-Player-Projections (private)

## Required configuration
- PostgreSQL 15+
- Python 3.11+, FastAPI and requirements-dev.txt
- Node 20+, Next.js frontend
- API_NBA_KEY (server secret), DATABASE_URL, ADMIN_TOKEN
- Never expose API_NBA_KEY in NEXT_PUBLIC_* or browser network calls

## DB migration order
sql/schema.sql -> sql/002_ingestion.sql -> sql/003_snapshots.sql

## Execution
Backend: cd backend && uvicorn app.server:app --host 0.0.0.0 --port 8000
Frontend: cd frontend && npm install && npm run build && npm start

## Release blockers to resolve and verify
1. Real API-NBA response shape: game status, team names, box score field names and season IDs.
2. PostgreSQL integration suite with TEST_DATABASE_URL; validate concurrency and UTC midnight rollover.
3. End-to-end daily ingestion: import completed games, then snapshot upcoming games before tipoff.
4. Backfill idempotency, complete-box-score checks and 20-call daily reserve.
5. Schedule 08:00 and 10:00 Europe/Athens (DST-aware); do not use fixed UTC offsets.
6. UI needs real player projections, filters, history and admin authentication.
7. Screenshot vision ingestion must use manual review and secure server-side vision key.
8. Weekly accuracy must compare saved pregame projections against pregame season baseline.

No production API calls or deployment have been performed.
