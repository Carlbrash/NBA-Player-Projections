# LOCKED — Player row visual, Electric Blue / jersey-first

This is a UI-only change to the player statistics table, NOT the game matchup cards.
Reference image: final approved electric-blue player row (jersey #34, portrait, name, team logo immediately AFTER name, MIL | MIL vs CHA).

## Exact order
Large glowing jersey number (NO team logo in the number slot) → player portrait → full name → team logo at end of name. Under name: team abbreviation | matchup. No PTS/REB/AST or other player statistics under the name. Keep PTS, REB, AST, 3PM, PRA, FORM L5 in their existing columns.

## Critical date-mode contract
- TODAY or any future scheduled game: values in stat columns MUST be **pregame projections** from saved projections table; show 80% interval beneath each projection. FORM L5 is the pregame form comparison.
- Any selected past/completed game: values in the SAME columns MUST be **actual stats from player_games for THAT specific game**. PTS, REB, AST, 3PM and PRA=PTS+REB+AST. Do not show season totals, season averages or projections in these cells. No projection intervals under actual values. FORM L5 shows em dash unless a separately documented pregame form snapshot is available.
- Use the game's actual status, not simply selected date, to determine mode: a delayed/incomplete game must not be presented as final.
- All players shown for final games must be linked by player_games.game_id. Do not show current roster players who did not play.
- Screenshot records are allowed when API record is not yet available; API supersedes screenshots.
- For future games, preserve pregame eligibility threshold (10 previous games) and distinguish players without projections.

## Data fields
playerId, gameId, name, jerseyNumber, teamCode, matchup, photoUrl, teamLogoUrl, pts, reb, ast, fg3m, pra, sdPts, sdReb, sdAst, sdFg3m, sdPra, formLast5, formChangePct.

## Integration instructions for Frank
1. Add PlayerStatRow.tsx/CSS and PlayerStatsTable.tsx/CSS under frontend/components.
2. Replace ONLY player rows/table rendering in the existing Today's Slate screen. Preserve date selector, matchup filters, search, sorting, navigation and other screens.
3. Data adapter: when game is final, fetch actual rows for selected game(s); when not final, fetch saved pregame projections. Do not mix actuals and projections in the same game's rows.
4. Map authentic portrait and logo URLs; never bake reference image into UI. Provide fallback portrait and jersey em dash for missing data. Team logos must appear AFTER name.
5. Keep table column alignment identical for both modes, including mobile horizontal scroll.
6. Validate a date with eight completed games, a date with upcoming games, and a mixed-status date.
7. No extra API-NBA calls per player or page view. Read PostgreSQL only.

## Acceptance checks
- #34 is at far left, then portrait, then full name, then Bucks logo to the right of name.
- Under name: MIL | MIL vs CHA.
- TODAY: PTS 26.7 plus 80% interval (example only).
- PAST GAME: PTS equals that player's actual PTS in that exact game, with no 80% interval.
- PRA equals the actual sum of PTS+REB+AST for past games.
- Sorting, searching, team/game filters work identically in both modes.
