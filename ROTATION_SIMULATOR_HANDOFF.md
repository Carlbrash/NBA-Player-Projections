# FRANK — Rotation Simulator patch (approved 2026-10-24)

## DO NOT REPLACE BASELINE
The existing pregame projection model, original projection snapshots, historical player_games, matchups and lineup components remain unchanged. The new engine is an **opt-in, side-by-side admin scenario**. Do not deploy until the integration tests pass.

## Approved rules
1. NBA regulation = 240 team-player minutes. ESPN historical rounded minutes (e.g. 243, 241) remain untouched. Normalize only forecast allocation, not stored box scores.
2. Only current-season games strictly before the selected tipoff (2026–27 => season=2026). Never use 2025–26 or later games.
3. OUT status from a verified upstream injury source if available; never assume API-NBA has injury coverage without checking. Admin can override after review.
4. A player OUT is always excluded from forecast team stats. An OUT with **less than 10 average minutes per actual appearance** does NOT trigger a compensatory redistribution; preserve other players' projected minutes and mark the forecast as partial (do not pretend the team total covers 240).
5. Material OUT (>=10 average minutes): admin may select up to TWO bench players (not existing starters) and specify **new total minutes** for each. Remaining minutes allocated to eligible teammates using current-season rotation weights, with max 48 minutes/player.
6. Player with **less than 5 TOTAL current-season minutes**: replace unstable per-minute rate with same-position teammates' pooled current-season PTS/MIN, REB/MIN, AST/MIN, 3PM/MIN; if same-position peers unavailable use pooled current-team rates. 5.0 minutes and above: own current-season rate. No prior season.
7. New stats = allocated minutes × rate. PRA = PTS+REB+AST. Team totals = sum available players only, never add OUT player. Do not modify original snapshots.
8. If the available roster/history cannot support a full 240-minute allocation, return partial=true and show observed current-season estimates; never invent player rates or silently fabricate missing minutes.
9. Manual admin scenarios are not confirmed starting lineups. Keep separate scenario_id and created_at; never overwrite actual game starters or historical stats.
10. All pages read PostgreSQL, not API-NBA per player. No additional NBA API calls required for scenario math.

## Files
- backend/app/rotation_experiment.py (pure calculations)
- backend/tests/test_rotation_experiment.py (offline tests)
- This handoff specification

## Integration requested
Build protected Admin > Rotation Simulator UI:
- select game/team, show OUT from verified feed (or manually flagged), show existing starters read-only
- select up to 2 BENCH replacements, enter NEW TOTAL minutes (not delta)
- compare BEFORE / AFTER by player for MIN, PTS, REB, AST, 3PM, PRA
- show team totals and 240-minute reconciliation; highlight partial scenarios
- save scenarios separately from projections/player_games, with admin identity, timestamp and source
- no production switch to experimental model without product owner approval

## Verified offline
The pure module was tested locally with pytest: 6 tests passed, including 240-minute conservation, <5-minute peer smoothing, no previous-season data, OUT threshold and <=2 replacements.
A local smoke test using the user's 24-row DAL current-season CSV yielded baseline 113.18 PTS and Flagg OUT with Clayton fixed at 25.3 MIN 100.77 PTS; these are **experimental**, not production predictions. The CSV was not committed.

## Acceptance / release gate
- Verify exact season mapping and current-season rows; never use future data.
- Run tests and a full PostgreSQL-backed integration test before enabling UI.
- Validate rate-smoothing with one-minute players and mixed-position rosters.
- Verify historical game results, snapshots and original baseline are byte-for-byte unchanged.
- Confirm admin overrides preserve starters and exact requested minutes.
- Explicit product owner approval before enabling in production.
