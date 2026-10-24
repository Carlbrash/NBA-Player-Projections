# LOCKED: Starting Lineups — Highlighted Roster Style 3

Approved by product owner. Replace ONLY the Starting Lineups section in Today's Slate, preserving the date selector, game cards, projections/actuals table, filters and navigation.

## Visual
Dark navy premium panel, Electric Blue integration, two team columns with authentic team logos and team-specific primary/secondary accents (e.g., Knicks orange/blue, Celtics green). Each starter row: **large luminous jersey number FIRST → square headshot SECOND → full player name THIRD → position or actual points FOURTH**. Five players per side where verified. No projected player stat totals in lineup rows.

## Crucial mode behavior
- Upcoming game with officially CONFIRMED starters: show 5 starters per team and position badge (PG, SG, SF, PF, C).
- Upcoming game without confirmed starters: do NOT invent a starting five or mark as CONFIRMED. Show unconfirmed/estimated state only if source and confidence are explicitly labeled, otherwise placeholder.
- Completed/past game: retain the ORIGINAL actual starting five for that specific game. Do NOT replace them with current roster, current projected starters or today's lineup. In the last badge, **replace position with actual PTS scored by that starter in that specific game** (e.g. 22 PTS). No season averages or projections. Preserve player number, portrait and name.
- Mode must depend on game status (final vs scheduled), not calendar date alone. Completed games on today's date also use actual points.
- If lineup history is missing, show NOT AVAILABLE, not a fabricated starting five. If a starter's points are missing, show em dash, not 0.

## Data contract
game_id; game status; teams: code,name,logoUrl,primaryColor,secondaryColor,record,side; starters: playerId,name,jerseyNumber,photoUrl,position,actualPts,isStarter,source.
Use one cached canonical player identity, real headshots, and real team logos. Never fetch API-NBA separately for each player or lineup UI render.

## Implementation
- Component: frontend/components/StartingLineups.tsx
- CSS: frontend/components/StartingLineups.css
- Wire to existing lineup source only if its starter flags are authoritative. Existing player_games schema does NOT record who started: a complete box score alone cannot identify the five starters.
- Persist immutable per-game starting five, team, starter flags, and source in a new game_starters table. A later roster change must not modify historical lineups.
- Join game_starters to player_games on (game_id,player_id) for actual points in finished games.
- Do not infer starters by minutes, points, or first five rows of a box score.
- No new API calls per player. Reuse existing source or bulk ingest starter metadata if available.
- Test both team layouts on desktop/mobile and confirmed/unconfirmed/historical states.

## Reference
Approved visual: Highlighted Roster Style 3, with jersey number moved before the photograph. Reference PNG is a design reference, not a source of verified player identities or lineup data.
