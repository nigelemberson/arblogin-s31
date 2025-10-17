# Changelog — A1 → A24e (highlights)

- **A1–A5**: Remove legacy Logout; wire placeholder Exit; restore spinbox arrows; early stability fixes.
- **A6–A12**: Exit wired to confirmation; removed border frame; initial Bet Card size attempts; Key dialog left unchanged.
- **A14–A18**: Exit visuals aligned with app; first pass at dialog isolation; intermittent Bet Card regressions.
- **A19–A21**: Fixed stray indent/syntax issues; prevented direct quits from button.
- **A22–A24b**: Robust mm→px sizing with DPI detection; minimum px fallback added.
- **A24c**: Clamped DPI range; ensured minimums for large readability.
- **A24d**: Removed accidental `dlg.setFixedSize(224, 133)` from Bet Card.
- **A24e**: Bet Card target changed to **110×80 mm** (DPI‑aware) with **420×300 px** fallback.
