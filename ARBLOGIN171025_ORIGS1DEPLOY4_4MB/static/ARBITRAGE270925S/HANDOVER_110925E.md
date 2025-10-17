# ARBITRAGE BOT — Handover & To‑Do (ARBITRAGE110925B)

_Last updated: 2025‑09‑11 (Asia/Manila)_

---

## Executive Summary

- **Status:** Close, but **not release‑ready**. Remaining issues are mainly UI consistency and a brittle plus/minus implementation that behaves differently across machines/themes.
- **Recommended approach:** Apply changes **one at a time**. This document includes a prioritized to‑do list, acceptance checks, and paste‑ready code snippets.

---

## What Works

- Core window, tables, and controls render.
- League label + dropdown present; “Fetch every” spinbox present; title font bump applied.
- A beginner‑friendly printable guide is available: **[Arbitrage_BOT_User_Guide_v3.rtf](sandbox:/mnt/data/Arbitrage_BOT_User_Guide_v3.rtf)**  
  (Uses **Team A/B/C** and **single‑letter variables**, ASCII only.)

---

## Release‑Blocking Issues

1) **Header alignment & clipping**
   - League dropdown text baseline can clip; arrow may be missing.
   - League dropdown width should **match** “Fetch every” width.
   - **No outer green frame** around the League + dropdown.
   - Title **“ARBITRAGE BOT”** must not truncate at common window sizes (e.g., 1366×768 and full‑screen).

2) **Spinboxes (all six)**
   - Plus/minus **must always show** on native orange buttons across PCs/themes.
   - Consistent height (e.g., **34 px**), proper right padding so values aren’t clipped.
   - Correct decimals (e.g., **2 dp** for “Fetch every”, “Fixed Fee”).

3) **Code hygiene**
   - `Dashboard._apply_plus_minus_icons()` is **called** in some builds but **not defined**, causing crashes.
   - Avoid temporary launchers/monkey‑patches; keep a **single `dashboard.py`** that runs cleanly.

---

## To‑Do (One‑by‑One, in Priority Order)

### A) Stabilize Plus/Minus Icons (Theme‑Proof)

**Goal:** Ensure **+ / −** always render on the orange up/down buttons for all six spinboxes on any PC/theme.

**Approach: use a style proxy (no QSS dependency on arrow images).**

Paste this near the imports in `dashboard.py`:

```python
from PyQt6.QtWidgets import QProxyStyle
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt

class PlusMinusProxyStyle(QProxyStyle):
    def _glyph(self, text, size=16):
        pm = QPixmap(size, size)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        f = QFont(); f.setBold(True); f.setPointSize(12)
        p.setFont(f); p.setPen(QColor("#000"))  # black; change if you prefer Ferrari green
        p.drawText(pm.rect(), int(Qt.AlignmentFlag.AlignCenter), text)
        p.end()
        return pm

    def standardPixmap(self, sp, opt=None, widget=None):
        if sp == self.SP_ArrowUp:
            return self._glyph("+", 16)  # 16px is a tasteful bump; try 15px if needed
        if sp == self.SP_ArrowDown:
            return self._glyph("-", 16)
        return super().standardPixmap(sp, opt, widget)
```

Then, **before** creating your main window (right after `app = QApplication(sys.argv)`):

```python
app.setStyle(PlusMinusProxyStyle(app.style()))
```

Also add a **safe stub** to avoid crashes where the old method is called:

```python
class Dashboard(...):
    ...
    def _apply_plus_minus_icons(self):
        # No-op: style proxy handles +/− universally.
        pass
```

**Acceptance checks**

- All six spinboxes show **+** (up) and **−** (down) on at least **two** different PCs.
- No missing arrows. No crash from `_apply_plus_minus_icons` call.

---

### B) Header Polish (League ⇄ Fetch Every; No Outer Frame)

**Goal:** Clean, single‑line header; matching widths; no clipping; title always visible.

**Implementation**

```python
# Heights
cmb.setFixedHeight(34)
spn.setFixedHeight(34)

# Widths: allow shrink but cap growth
cmb.setMinimumWidth(160); cmb.setMaximumWidth(200)
spn.setMinimumWidth(140); spn.setMaximumWidth(200)

# Combo QSS to avoid baseline clipping and ensure room for arrow
cmb.setStyleSheet(
    "QComboBox { padding-top:2px; padding-bottom:2px; padding-right:26px; }"
    "QComboBox::drop-down { width:22px; border:0; margin-right:4px; }"
)

# Tighten header spacing/margins so the title fits
layT.setSpacing(6)
layT.setContentsMargins(8, 4, 8, 4)

# Ensure the title label gets space
layT.addStretch(1)
```

**Notes**

- Keep **only** the label (“League”) and the dropdown inline—**no outer green frame**.
- If space is still tight, reduce **spacing** first; avoid shrinking the title.

**Acceptance checks**

- At **1366×768** and full‑screen: no horizontal scroll; full “ARBITRAGE BOT” visible.
- League dropdown baseline OK; right‑side arrow visible; width matches “Fetch every”.

---

### C) Spinbox Sizing/Format

**Goal:** Consistent height, visible decimals, and comfortable padding.

```python
for w in (spnSecs, inStake, inOddsA, inOddsB, inComm, inFee):
    w.setFixedHeight(34)

# Decimals (examples)
spnSecs.setDecimals(2)
inFee.setDecimals(2)

# Optional global padding if needed (applied after QApplication):
app.setStyleSheet(app.styleSheet() + \"\"\"
QDoubleSpinBox { padding-right: 30px; }   # use 32px if icons are 16px and look tight
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 22px; }
\"\"\")
```

**Acceptance checks**

- Values like `120.00` or `120.00%` are **not clipped**.
- Mouse, keyboard, and wheel behavior unchanged.

---

## How to Run (Clean Path)

- Prefer a **single** `dashboard.py` with:
  - `PlusMinusProxyStyle` applied at app startup,
  - header fixes in `_build_ui`,
  - `_apply_plus_minus_icons` stubbed (no‑op).

Launch as usual:

```powershell
python .\start_dashboard.py
```

---

## Testing Checklist (Fast)

1) **Launch:** No exceptions.
2) **Header (1366×768 & full‑screen):** No horizontal scroll; “ARBITRAGE BOT” intact.
3) **League + Fetch Every:** Same width; no clipping; arrow visible; no outer frame.
4) **Spinboxes (six):** +/− present and clearly visible; values not clipped; proper decimals.
5) **Controls:** Refresh/FETCH/Auto toggle respond; status messages appear promptly.

---

## Risks & Fallbacks

- **QSS overrides:** Some themes or code may override stylesheet rules. The **style proxy** bypasses this by replacing standard arrow pixmaps at the style level.
- **Hi‑DPI scaling:** 16 px is usually safe at 125–150%. If icons feel too small, try **17–18 px** and set button width to **22–24 px**.
- **Missing methods:** Keeping the `_apply_plus_minus_icons` **no‑op** ensures legacy calls do not crash.

---

## Deliverables & References

- Printable guide (v3): **[Arbitrage_BOT_User_Guide_v3.rtf](sandbox:/mnt/data/Arbitrage_BOT_User_Guide_v3.rtf)**
- This handover: **Handover & To‑Do (Markdown)**

---

## Notes on Math (as used in the guide)

- **Two outcomes (no fees)**  
  Let total stake **S**, odds **X** (Team A), **Y** (Team B).  
  `Sum = (1/X) + (1/Y)`  
  `U = S * ((1/X) / Sum)` ; `V = S * ((1/Y) / Sum)`  
  `R = S / Sum` ; `P = R - S`

- **Fees**  
  Winner‑only commission on winnings at rate **C**: `M = (1 - C) * O + C`  
  Winner‑only payout commission at rate **K**: `M = (1 - K) * O`  
  Turnover fee **T** and fixed fee **F** are **constant costs**: subtract `T * S` and `N * F` after the split.

---

## Version / Environment Targets

- **Python:** 3.13
- **PyQt:** PyQt6 (Qt 6)  
  Avoid attributes not present in your PyQt build; use the style proxy to avoid resource/QSS fragility.

---

## Change Log (recent)

- Consolidated guidance into a single handover document.
- Added **style proxy** solution for +/− to be theme‑proof.
- Clarified header width matching and clipping fixes.
- Provided acceptance checks and test checklist.
