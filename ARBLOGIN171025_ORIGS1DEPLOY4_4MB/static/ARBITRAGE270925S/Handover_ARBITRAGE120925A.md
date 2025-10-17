# Handover — SPORTS ARBITRAGE BOT
**From:** ARBITRAGE110925E → **To:** ARBITRAGE120925A (Version **F** as baseline)

---

## 1) Current Baseline & Working Behaviors (kept for Version F)
- **Start script:** `start_dashboard.py`
- **Main UI:** `dashboard.py` (flat package; **no nested folders**)
- **League selector:** works as before
- **Quota pill:** `Quota: {used}/{last} • {remaining} left`
  - `used` = `x-requests-used`
  - `last` = `x-requests-last` (per-call cost). Falls back to `?` if header absent.
  - `remaining` = `x-requests-remaining`
  - **No hover tooltip.** **No click action.**
- **Green API band (Table 1 strip):** shows **only** results from **Fetch Now (API)**; not changed by UI-only refresh.
- **Buttons (split):**
  - **Fetch Now (API):** makes the network request; updates Table 1, the **green API band**, and the **quota pill**.
  - **Refresh Odds / Arbs:** **UI-only**; repaints Table 1 & 2, updates **Table 2 label** to `Last refresh (UI): YYYY-MM-DD HH:MM:SS`, and posts bottom status `Refresh complete (UI only)`. **No network call.**

---

## 2) What Changed Since Early E
1) Quota pill cleaned:
   - Tooltip removed; click disabled.
   - Text shows per-call cost instead of unknown limit.
2) Button split finalized:
   - **Fetch Now (API)** = network + green band + pill.
   - **Refresh** = UI-only + timestamp on Table 2 label + bottom status.
3) **Green API band** protected from **Refresh**.

---

## 3) Acceptance / Smoke Tests
1) Launch app → Quota pill may show `demo` until first fetch.
2) Click **Fetch Now (API)** →
   - Table 1 updates with new rows.
   - Green band: `Last reload (API): ok | x-requests-used:… | x-requests-remaining:… | x-requests-last:…`
   - Pill: `used/last • remaining` (numbers advance).
3) Click **Refresh Odds / Arbs** →
   - No change in green band or pill.
   - Bottom-left status: `Refresh complete (UI only)`.
   - Table 2 label: `Last refresh (UI): YYYY-MM-DD HH:MM:SS`.
4) Hover/click Quota pill → nothing happens (by design).

---

## 4) Carryover TODOs (for ARBITRAGE120925A)
- **A. Offline arbs recompute on Refresh (no API):**
  - Rebuild Table 2 from cached Table‑1 rows to show current arbitrage opportunities without a network call.
  - *Acceptance:* pressing **Refresh** updates Table 2 values deterministically with no quota usage.
- **B. Header order stability (minor):**
  - Ensure green band always prints `used, remaining, last` in that order (normalize keys on parse).
- **C. Optional: hide green API band unless error:**
  - When last call is `ok`, keep the band collapsed/hidden; display only on error or when toggled.
- **D. Configurable plan limit (optional):**
  - Support `plan_limit` in `config.json` to show `used/plan_limit` if `x-requests-last` is missing.
- **E. Export & Audit Log sanity pass:** ensure file paths remain flat; confirm “Export” and “Audit Log” still work with Version F.
- **F. Error/edge UX:** confirm cooldowns and disabled states on fast repeat clicks; friendly dialogs on failures.
- **G. Auto modes:** verify **Auto Fetch** / **Auto Refresh** / **Live 1‑min** timings still align with quota strategy.
- **H. Theme consistency:** keep message dialogs readable without altering the app’s capsule/pill visuals.

---

## 5) Risks / Notes
- Different APIs sometimes vary header **order**; we will explicitly order them at render time.
- Odds API header `x-requests-last` may be absent → pill shows `?` as designed.
- Keep the package **flat** (no nested folders) when producing zips.

---

## 6) Next‑Tab Setup (ARBITRAGE120925A)
- You’ll send **Version F** zip as the new baseline.
- I will:
  1) Verify flat structure, `start_dashboard.py` entry, and run smoke tests (Section 3).
  2) Implement **TODO A** (offline arbs recompute on Refresh) as the first single change.
  3) Proceed to **TODO B** (header order) as the second single change.
- Deliverables will be **single drop‑ins** (`dashboard.py`) or a **flat full zip** when required—always compiled/validated first.

---

## 7) Changelog (E → F)
- Quota pill: no tooltip, no click; text switched to `used/last • remaining`.
- Button split: Refresh = UI‑only; Fetch Now = API.
- Table 2 label gains timestamp on Refresh.
- Green API band protected from Refresh.

---

**Ready for ARBITRAGE120925A** — awaiting Version F zip to begin TODO A (offline arbs recompute on Refresh).

