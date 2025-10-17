
# TODO List (carried forward)

## Immediate
- Verify **orange Bet Card button** remains fully functional in release conditions.
- Confirm **no green badge** present at bottom of window.
- Ensure UI styles (plus/minus buttons, pill colors, frames) remain consistent with "golden" GG reference.

## Medium Term
- Integrate league-switch one-click (EPL/MLS/A-League/India).
- Add optional verbose console runner.
- Checklist before placing bets: re-open books, confirm prices, stake rounding, rerun calculation if prices moved.
- Keep table labels consistent across GUI (swap/update "Table 1" and "Table 2" labels as planned).

## Longer Roadmap
- Regions="uk" option for API fetches.
- Auto-refresh 60–90s interval.
- Improve reliability with requests.Session + gzip, optional parallel fetch.
- Add visible error banner (last fetch error).
- Introduce "Safe Mode" diagnostics (skip network, instant UI).
- Requirements.txt with pinned versions; add version string + CHANGELOG.
- Batch/script helpers: .bat launcher, backup/restore scripts.
- One-button action: fetch → compute stakes → open bet_card.txt.
- Smoke test script to verify config load, provider selection, cache write.

