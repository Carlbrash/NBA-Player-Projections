# FRANK — Starting Lineups UI / final approved design

Use the approved Highlighted Roster Style 3 visual with this exact row order:
**JERSEY NUMBER → SQUARE PHOTO → PLAYER NAME → POSITION/POINTS**.

For upcoming games, show confirmed starters with position (PG/SG/SF/PF/C). For finished games, retain that game's true starting five and show actual PTS from that game's player_games instead of the position. Do not use current rosters, estimated starters, or season averages.

Repository implementation:
- frontend/components/StartingLineups.tsx
- frontend/components/StartingLineups.css
- backend/app/lineups.py
- sql/006_game_starters.sql
- STARTING_LINEUPS_DESIGN_LOCK.md

Add endpoint GET /api/games/{game_id}/lineups using get_game_lineups. Add team colors, real logo/headshot URLs and jersey numbers through existing cached metadata. Ensure source supplies verified historical starter identities. Do not infer starter status from box-score row order or minutes. If source lacks verified starters, display NOT AVAILABLE.

Use reference mockup as a style guide, not a data source. Preserve all other Today's Slate components. No external API calls on each page view.
