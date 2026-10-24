# Release checklist for Frank

Status: NOT VERIFIED / NOT READY FOR PRODUCTION

## Local verification
1. Create .env with POSTGRES_PASSWORD, API_NBA_KEY and ADMIN_TOKEN; never commit secrets.
2. Run docker compose build and docker compose up -d.
3. Verify http://localhost:8000/health and http://localhost:3000.
4. Run PostgreSQL integration tests with isolated TEST_DATABASE_URL.
5. Run frontend build and test all five pages.
6. Validate API-NBA response mapping using one authorized sample call (after explicit go-ahead).
7. Verify newest-first 2026-27 backfill and one box-score call per game.
8. Verify UTC date boundaries and 08:00/10:00 Europe/Athens scheduler.
9. Verify screenshot image extraction and editable review before enabling.
10. Do not enable public deployment until authentication, request caps, and ingestion correctness pass.

## Known blockers
- Vision LLM extraction not connected.
- Scheduler code exists but no active external 08:00/10:00 cron.
- Current backend still needs real API schema integration verification.
- Daily job and backfill need end-to-end tests.
- API call reservation requires UTC rollover and failure-path validation.
