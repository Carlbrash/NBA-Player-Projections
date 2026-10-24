# LOCKED UI: NBA Matchup Cards — Electric Blue (Concept 1)

Approved: Electric Blue 3D-logo visual. Applies ONLY to the matchup selector strip on Today's Slate and historical-date views. Do not redesign the rest of the dashboard.

## Exact behavior
- Scheduled / not started: show both NBA team logos, 3-letter abbreviations, current-season W–L under each logo, scheduled tipoff in the center top, VS in center, and **current-season H2H record** in smaller text below.
- If the teams have not met this season: display NO H2H, not 0–0 presented as an actual score.
- Final game: replace scheduled tipoff with FINAL and center VS with the final game score (away : home); keep the current-season H2H beneath.
- Never show invented H2H or placeholder score as real data.
- Team record and H2H are **as-of selected game's tipoff**, not final season standings. For historical dates, exclude all later games. For an upcoming game, exclude its result. H2H must be oriented away–home, irrespective of who hosted earlier meetings.
- NBA games can cross midnight in Europe/Athens: preserve UTC tipoff and convert to user's displayed timezone consistently.
- Selectable cards must filter the player projection table; selected game gets stronger blue outline. 'ALL' selector remains.
- Card compact target: 222 px width desktop, 205 px mobile, 126 px minimum height, horizontal scroll for large slates. Preserve team logo aspect ratio, never distort or bake logos into the background.
- Colors: navy #061326 / #0a2039; electric border #2187ff; neon mint #10edbb; text #f4f8ff.
- Real NBA logo images must be sourced from properly licensed assets or existing provider's official team logo URLs. Do NOT crop/reuse generated mockup logos as production assets.

## Deliverables
- React component: frontend/components/MatchupCard.tsx
- Styling: frontend/components/MatchupCard.css
- Visual reference images are provided separately in the handoff ZIP; mockups only.
- Map existing backend data into MatchupCardData, with records/H2H computed from games in PostgreSQL.
- Show loading skeletons for missing data; no extra API calls per card.

## Acceptance
1. Upcoming game with no H2H: time, VS, NO H2H.
2. Upcoming game with 1–2 H2H: time, VS, 1–2.
3. Completed game: FINAL, final points, H2H.
4. Season W–L and H2H never include games after selected tipoff.
5. Click card filters players; ALL restores entire slate.
6. At least 8 cards scroll smoothly at 1440px and on mobile.
