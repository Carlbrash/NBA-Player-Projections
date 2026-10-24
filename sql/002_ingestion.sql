CREATE TABLE IF NOT EXISTS ingestion_state (
 game_id BIGINT PRIMARY KEY REFERENCES games(id) ON DELETE CASCADE,
 status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','claimed','complete','failed')),
 claimed_until TIMESTAMPTZ,
 attempts INTEGER NOT NULL DEFAULT 0,
 completed_at TIMESTAMPTZ,
 last_error TEXT,
 updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ingestion_state_pending_idx ON ingestion_state(status,claimed_until);
CREATE TABLE IF NOT EXISTS api_request_log (
 id BIGSERIAL PRIMARY KEY,
 attempted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 endpoint TEXT NOT NULL,
 game_api_id BIGINT,
 outcome TEXT NOT NULL,
 error TEXT
);
