# API-NBA call minimization policy

Mandatory implementation requirements:
- Fetch season schedule once with GET /games?league=standard&season=2026, after verifying season IDs. Check response completeness and pagination before assuming one call covers all games.
- GET /players/statistics?game={id} once per finished game, returning both teams' players; never call per player.
- Persist normalized team, player, game and box-score records in PostgreSQL. Skip already validated box scores; retry only missing, incomplete or explicitly invalidated records.
- Compute all projections, form, opponent factors, standard deviations, and probabilities locally. Never use API calls for derived statistics.
- Daily jobs should reuse cached schedule where valid and fetch only necessary dates/games; avoid repeating season-wide lists.
- Deduplicate requests across jobs using database-backed claim/lease and enforce one shared 90-call UTC daily cap with at least seven seconds between calls.
- Reserve calls for daily updates before backfill; backfill priority: 2026-27 newest-first, then 2025-26.
- Log each attempted API call, endpoint, game ID, result, and reason, without logging API keys.
- No historical API calls until rate-limit concurrency and integration tests pass.
