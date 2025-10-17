# Handover — ARBITRAGE240925A_H (Full App, visual-only, Settings wired)

- Part 2 normalization re-applied across all `.py` (tabs→spaces, LF endings, trailing-space purge, empty-block `pass`).
- **Audio fully purged** (no beep, winsound, QtMultimedia).
- **T2 flashing (visual-only) integrated**: OR logic, color cues; safe restore on refresh.
- **Settings Edge/Profit wired in-code** using existing keys (`ding_edge_min`, `ding_profit_min`).
- Init hooks added in `__init__` to start flasher and bind Settings.

Build time: generated automatically.
