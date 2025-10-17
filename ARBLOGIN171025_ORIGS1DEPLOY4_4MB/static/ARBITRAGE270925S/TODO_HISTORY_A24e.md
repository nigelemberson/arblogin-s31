# Historical TODO / Next-steps (prioritised)

## P0 – Keep stable
- Keep **dialog styles scoped**. Do not introduce global `QDialog{}` rules.
- Preserve **Bet Card mm→px** sizing block; if you need exact pixels, replace with `setFixedSize(W,H)`.

## P1 – Short term improvements
- Replace PNGs triggering `libpng` warnings with clean RGBA exports.
- Centralise colours / radii / spacing in a small theme helper to avoid style drift.
- Add keyboard accelerators for the six spinboxes (e.g., Shift=×5, Ctrl=×10).

## P2 – Feature candidates
- **Row highlight/breathe** in Table‑2 for good arbs (thresholds from Edge%/Profit). Use a timer and a short cooldown to avoid flicker.
- Export Bet Card to clipboard in both **plain text** and **JSON** for automation.

## QA checklist for each drop
- Exit dialog opens 224×133, **No** cancels, **Yes** exits.
- Bet Card always opens ≈ target size on each monitor/scaling.
- All six spinboxes show +/- and respond to clicks and wheel.
- No app‑wide stylesheet contains `QDialog` rules.
