# ARBITRAGE180925L — Handover

**Build:** L (clean)
**Source base:** ARBITRAGE180925A (original)
**What changed for L:**
- Removed nested `ARBITRAGE120925GG` folder (no duplicate app inside).
- Kept your original working `dashboard.py` and `start_dashboard.py` as provided.
- No other files changed. GUI and behavior unchanged.
- Plus/minus are handled exactly as in your originals.

## How to run
1. Open PowerShell inside the `ARBITRAGE180925L` folder.
2. Run:
   ```
   python start_dashboard.py
   ```

## Standing TODOs (carry-forward list)
- One-click league switcher with clear pill state (EPL/MLS/A-League/India).
- Verbose runner option to print each step in PowerShell.
- Pre-bet checklist workflow:
  - Re-open target books and re-confirm prices.
  - Round stakes to book increments.
  - If any price moves, re-run console + stake calc.
- GUI labels consistency check:
  - “Table 1: Live Feed” / “Table 2: Arbitrage Opportunities” naming kept consistent.
- Extract window/app icon into `/assets/icon.ico` (avoid embedded blobs).
- Requirements file with pinned versions; add version string + CHANGELOG.
- Startup helpers: BAT launcher, config backup/restore.
- One-button flow: fetch → compute → open `bet_card.txt`.
- Smoke test script: config load, provider selection, key presence, fetch, cache write.
- Speed & reliability ideas (optional):
  - `requests.Session` + gzip; 60–90s auto-refresh; disk cache warm start.
  - Optional parallelism per region/book; Safe Mode (skip network) & error banner.

## Historical TODOs (last 30 days — condensed)
- **2025‑09‑17 (ARBITRAGE170925)**: Stabilize “Use Selection” across T1/T2; restore plus/minus; protect Bet Card; table highlight hop bug noted; quota pill & auto‑refresh regressions.
- **2025‑09‑16 (ARBITRAGE160925)**: Merge from GG baseline; align plus/minus, orange styling; splitter consistency.
- **2025‑09‑15 (ARBITRAGE150925)**: Focus on Use Selection stuck-in‑T2; missing T2 highlight; Bet Card blank window; multiple interim merges.
- **2025‑09‑14 (NEWBUILD v6 transplant)**: Header/icon/size tuning; calculator reinstated; logout/audit dialogs styled.
- **2025‑09‑13 (misc fixes)**: Logout & Audit window sizing/styling; g-series patches; instability noted.
- **2025‑09‑12 (ARBITRAGE120925GG)**: Golden master snapshot for style and plus/minus behavior.

## Known Good Anchors
- `ARBITRAGE120925GG` — style / plus-minus baseline.
- `ARBITRAGE160925A/B` — first stable two‑table highlights.
- `ARBITRAGE170925A` — working launch with later Bet Card tweaks.
- **`ARBITRAGE180925L`** — current clean working build (this package).

---
**Note:** No removal of the green “Bet Card” rectangle was performed in this build. Any exploration of that change must be explicitly requested and delivered as a separate package.
