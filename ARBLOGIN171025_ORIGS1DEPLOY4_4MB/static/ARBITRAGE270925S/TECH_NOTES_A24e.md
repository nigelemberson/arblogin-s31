# Technical Notes (A-series through A24e)

This document captures the issues encountered and the fixes applied so the next engineer does not repeat the cycle.

## Root causes seen
- **Global QSS for `QDialog`** bled into unrelated dialogs (Bet Card, Key) — caused size and style regressions.
- **Handler mismatches** (`_open_exit_dialog` missing or miswired) → crashes.
- **Stray size call** (`dlg.setFixedSize(224, 133)`) accidentally copied into Bet Card after Exit refactor.
- **Windows DPI quirks** with multi‑monitor scaling → mm‑sized dialogs not matching expectations.
- **Minor syntax/indent errors** from manual merges (extra `)`, dedents).

## Durable patterns put in place
- **Scoped styles**: Apply dialog QSS only via `dlg.setStyleSheet(...)` for that dialog.
- **Sane sizing**: Convert millimetres to pixels using the **current screen** DPI and clamp to avoid weird reports; add a **minimum px fallback**.
- **Exit safety**: Never call `quit()` from a button — always gate it behind a modal `QDialog.exec()` result.

## Implementation highlights
- **ExitDialog** (`exit_dialog_custom.py`) uses a small local style:
  - Background `#0b0f0f`, title green injected from dashboard (`_accent_green_hex_from_table()`), body text colour `#e6e6e6`.
  - Buttons in the orange family: normal `#ff8c2a`, hover `#ffa64d`, pressed `#ff7a00`.
- **Bet Card sizing** (A24e):
  - Target: **110×80 mm** → px via `screen.logicalDotsPerInch()`.
  - Clamp DPI: `<80 → 96`, `>200 → 120` (protects against odd driver values).
  - Minimum px fallback: `420×300` to guarantee readability.

## “If this happens, do this”
- **Bet Card tiny again** → search for any `dlg.setFixedSize(224, 133)` and remove; re‑run.
- **Exit exits immediately** → ensure `_open_exit_dialog()` returns only on `Accepted` and that the button calls this method (not `quit()` directly).
- **Spinbox +/- missing** → check QSS for `QAbstractSpinBox::up-button/down-button` being hidden or a sibling widget covering the right edge.

## Useful snippets
**mm → px helper**
```python
def mm_to_px(mm, widget):
    from PyQt6.QtGui import QGuiApplication
    h = widget.window().windowHandle() if hasattr(widget.window(), "windowHandle") else None
    scr = h.screen() if h else QGuiApplication.primaryScreen()
    ppi = float(scr.logicalDotsPerInch()) if scr else 96.0
    return int(round(mm * ppi / 25.4))
```

**Scoped dialog style skeleton**
```python
dlg.setStyleSheet("""
QDialog, QDialog * { background: #0b0f0f; border: none; }
QLabel#title { color: %ACCENT%; font-weight: 800; }
QLabel#body  { color: #e6e6e6; }
QPushButton  { background: #ff8c2a; color: #111; font-weight: 700; border-radius: 10px; padding: 6px 12px; }
QPushButton:hover  { background: #ffa64d; }
QPushButton:pressed{ background: #ff7a00; }
""")
```

