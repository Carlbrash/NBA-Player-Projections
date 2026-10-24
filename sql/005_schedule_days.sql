CREATE TABLE IF NOT EXISTS schedule_day_state (
 schedule_date DATE PRIMARY KEY,
 completed_at TIMESTAMPTZ NOT NULL,
 games_count INTEGER NOT NULL DEFAULT 0
);
