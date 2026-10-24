# IMPLEMENTATION PROMPT FOR FRANK — LOCKED PLAYER ROW

Implement the approved Electric Blue player-row redesign in the existing NBA Player Projections Today's Slate UI. The existing date selector and matchup cards must remain unchanged.

Use the following repository files as the source of truth:
- frontend/components/PlayerStatRow.tsx
- frontend/components/PlayerStatRow.css
- frontend/components/PlayerStatsTable.tsx
- frontend/components/PlayerStatsTable.css
- backend/app/player_rows.py
- PLAYER_ROW_DESIGN_LOCK.md

IMPORTANT: The approved layout is **large luminous jersey number on the LEFT, player headshot NEXT, full name NEXT, team logo at the END of the name**. Under the name show team abbreviation and the specific matchup. The team logo MUST NOT appear in the number slot or under the name. Maintain the existing PTS, REB, AST, 3PM, PRA and FORM L5 columns.

CRITICAL DATA MODE: For scheduled games show saved pregame projections and 80% ranges. For finished games selected through the historical date picker, show ACTUAL PTS/REB/AST/3PM/PRA from player_games for the selected game only, with no ranges or season averages. Do not choose mode merely by calendar date; use actual game status. A completed game in today's date must also show actuals.

Backend route required: expose game_player_rows(db, game_id) via GET /api/games/{game_id}/player-rows; add the same mode contract for the ALL-games view. Map real headshots, jersey numbers, team logos and matchup labels using cached data/provider assets, without a per-player API call. If data are absent, use safe fallbacks rather than fabricating them.

Do not use the design PNG as a page background. The PNG is a visual reference; render responsive real HTML/CSS. Integrate, test and deploy only after verifying both modes and that sorting/filtering remains intact.
