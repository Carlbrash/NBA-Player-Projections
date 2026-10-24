# NBA Box Score Screenshot — Vision AI implementation specification

## Selected reader
Use **OpenAI GPT-4.1 with image input** (Vision) through a **server-side OpenAI API integration**. Store the credential as `OPENAI_API_KEY` in server secrets. The vision model must never be called from the browser. Keep the model configurable (`VISION_MODEL`) so it can be upgraded without rewriting the ingestion pipeline. No OpenAI key is currently configured; this is the implementation specification, not a claim that extraction is active.

## Workflow
1. User selects NBA game and uploads one or more PNG/JPG screenshots (max 8 MB each). Allow images for both teams and multiple panels.
2. Server sends each image to the configured vision model with strict structured JSON output. Request teams, team totals and all players who participated; skip DNP and inactive rows. Never invent obscured numbers. Mark missing or ambiguous values as null and report them.
3. Extract: name, minutes, PTS, FGM/FGA, 3PM/3PA, FTM/FTA, REB, AST, TOV, STL, BLK, plus/minus, team identifier and team totals.
4. Validate player points = 2*FGM + 3PM + FTM; nonnegative integer box-score counts; minutes in MM:SS; both teams represented; game/team identity matched to local database. Team totals may not always equal summed player rebounds due to team rebounds: **flag discrepancies for review, never silently reject on that rule alone**.
5. Normalize names (lowercase, remove accents and dots), match by provider ID if known; otherwise offer candidate player matches and explicit create-new action. Never silently merge ambiguous names.
6. Display an editable review table, highlighting mismatches in red, and require an explicit Confirm & Save action. Do not persist extracted player_games before confirmation.
7. Save `source='screenshot'` transactionally. Validated API box scores take precedence; never overwrite an existing `source='api'` row.
8. Recompute future projections locally after confirmation; preserve immutable historical pregame snapshots. Log ingestion and validation errors in update_log.

## Vision prompt
You are extracting an NBA box score from screenshot images. Return only JSON matching the requested schema. Include both teams if shown. Extract every player who played, omitting DNP/inactive rows. Do not estimate, guess, or fabricate obscured values. Use null for unreadable values and include warnings. Preserve numeric accuracy, especially FGM/FGA, 3PM/3PA, FTM/FTA, PTS, REB, AST, STL, BLK, TOV, +/- and minutes.

## Required JSON shape
{
  "teams": [
    {
      "name": "Team name",
      "totals": {"pts": 0, "reb": 0, "ast": 0},
      "players": [
        {
          "name": "Player name", "min": "00:00",
          "pts": 0, "fgm": 0, "fga": 0,
          "fg3m": 0, "fg3a": 0, "ftm": 0, "fta": 0,
          "reb": 0, "ast": 0, "tov": 0,
          "stl": 0, "blk": 0, "plus_minus": 0
        }
      ]
    }
  ],
  "warnings": []
}

## Privacy and cost
Send only the uploaded box-score image to the vision service. Do not send secrets, internal database records or unrelated user information. Show extraction errors without exposing credentials. Meter vision usage separately from the API-NBA 90-call/day quota.

## Release acceptance
Test with actual screenshots for both teams, cropped/blurred rows, DNP, duplicate names, incorrect points arithmetic, and manual edits. Ensure no database write occurs before confirmation. The current screenshot implementation is manual JSON review only and does not yet call the vision model.
