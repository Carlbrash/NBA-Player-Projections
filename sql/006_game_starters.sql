CREATE TABLE IF NOT EXISTS game_starters (
 game_id BIGINT NOT NULL REFERENCES games(id) ON DELETE CASCADE,
 player_id BIGINT NOT NULL REFERENCES players(id),
 team_id BIGINT NOT NULL REFERENCES teams(id),
 position TEXT,
 source TEXT NOT NULL,
 confirmed BOOLEAN NOT NULL DEFAULT false,
 recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 PRIMARY KEY(game_id,player_id)
);
CREATE INDEX IF NOT EXISTS game_starters_game_team_idx ON game_starters(game_id,team_id);
