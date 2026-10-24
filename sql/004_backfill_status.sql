-- Normalize provider completion statuses for ingestion queries.
-- This migration does not alter any provider records.
CREATE INDEX IF NOT EXISTS games_season_date_idx ON games(season,date_utc DESC);
CREATE INDEX IF NOT EXISTS player_games_game_idx ON player_games(game_id);
CREATE INDEX IF NOT EXISTS player_games_player_idx ON player_games(player_id);
