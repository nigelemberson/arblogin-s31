# Project Handover — ARBITRAGE210925 (A24e)

**Current drop:** A24e (Bet Card ≈ *110×80 mm*, Exit 224×133)  
**Entry point:** `start_dashboard.py` → `dashboard.py`  
**Primary modules:**  
- `dashboard.py` — main window & all wiring (buttons, tables, dialogs).  
- `exit_dialog_custom.py` — custom Exit confirmation dialog (scoped QSS only).

## Run
```powershell
python start_dashboard.py
```

## Code map (practical)
- **Exit button →** `Dashboard._open_exit_dialog()` → `ExitDialog(...)` (from `exit_dialog_custom.py`).  
  *Exits only when dialog returns* `Accepted`.
- **Bet Card button →** `Dashboard._open_bet_card()` → creates `QDialog` + applies **mm→px** sizing block.  
- **Accent colour** (green) → `Dashboard._accent_green_hex_from_table()` (reads live from Table‑1 highlight).  
- **Spinboxes** (6 inputs) → created in `dashboard.py` with **visible +/-** button symbols (do not hide in QSS).

## Key decisions
1. **No global `QDialog` styles**. All dialog QSS is **local** to the instance to prevent cross‑pollution (Bet Card once shrank when Exit styles were global).
2. **Dialog sizing** uses **mm→px** on the **active monitor DPI** with clamped DPI and a minimum px fallback. This makes sizes stable across Windows scaling / multi‑monitor setups.
3. **Typography** for Exit dialog body text uses `self.tblLive.font()` to track the same face/size as the Table‑1 rows (e.g., “Arsenal”).

## What’s locked right now
- **Exit dialog** — 224×133, no border frame, title = accent green, body text matches Table‑1 font.  
- **Bet Card** — ≈ **110×80 mm** (A24e); sensible minimum fallback (**420×300 px**).  
- **Spinboxes** — +/- arrows visible on all six.

## Where to change sizes
- **Bet Card:** in `_open_bet_card()` locate the block that begins `# Enforce Bet Card size`.  
  - Change the **110/80 mm** values or hard‑set pixels: `dlg.setFixedSize(W, H)`.
- **Exit:** in `exit_dialog_custom.py` constructor: `self.setFixedSize(224, 133)`.

## Known non‑blocking items
- A couple of PNGs log `libpng` warnings; replace those images when convenient.
- If a future stylesheet touches `QAbstractSpinBox` sub‑controls, arrows may hide — keep QSS narrow.

## Recovery recipe (if a dialog goes tiny again)
1. Search for stray `dlg.setFixedSize(224, 133)` in **`_open_bet_card()`** and delete if present.
2. Ensure there’s no app‑wide `QDialogEllipsis` in a global style string.
3. Keep the mm→px block **after** the dialog layout and QSS, and before `dlg.exec()`.

