CREATE UNIQUE INDEX IF NOT EXISTS projections_one_pregame_snapshot
ON projections(player_id,game_id);
CREATE TABLE IF NOT EXISTS schedule_fetch_state (
 season INTEGER PRIMARY KEY, fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 games_count INTEGER NOT NULL, complete BOOLEAN NOT NULL DEFAULT false
);
CREATE TABLE IF NOT EXISTS api_request_claims (
 request_key TEXT PRIMARY KEY, claimed_until TIMESTAMPTZ,
 completed_at TIMESTAMPTZ, status TEXT NOT NULL DEFAULT 'pending'
);
