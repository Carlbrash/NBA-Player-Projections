# NBA Player Projections

Standalone pregame NBA player projection application. No ASSOS365 or JDTool dependencies.

## Status
Phase 1 foundation under development. **Not production-ready.** No deployment or scheduled jobs are active.

## Architecture
- FastAPI backend
- PostgreSQL database
- API-NBA (API-Sports) data source
- Next.js frontend planned

## API safety
API key is supplied via `API_NBA_KEY` environment variable, never committed. Shared daily quota must be persisted in PostgreSQL before enabling workers; 90 calls/day and 7 seconds minimum between requests. Do not run multiple independent workers against the same quota.

## Next steps
Implement and test migrations, API client, ingestion and quota concurrency, then backfill and dashboard. Validate upstream response schemas before production.
