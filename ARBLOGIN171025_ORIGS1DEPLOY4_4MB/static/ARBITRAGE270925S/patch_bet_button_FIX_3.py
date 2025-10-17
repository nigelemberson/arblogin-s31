# patch_bet_button_FIX_3.py
# Usage: python patch_bet_button_FIX_3.py
# Patches local dashboard.py to wire the orange "Bet Card" button to _open_bet_card()

from pathlib import Path
import re, sys

DASH = Path("dashboard.py")
if not DASH.exists():
    print("ERROR: dashboard.py not found in current folder"); sys.exit(1)

src = DASH.read_text(encoding="utf-8", errors="ignore")

# 1) Ensure the creation site wires the button
pattern = r'(self\.btnBetCard\s*=\s*add_btn_calc\(\s*["\\\']Bet Card["\\\']\s*\).*)'
if re.search(r'btnBetCard\.clicked\.connect\s*\(\s*self\._open_bet_card\s*\)', src):
    already_direct = True
else:
    already_direct = False

def insert_after_creation(s: str) -> str:
    m = re.search(pattern, s)
    if not m:
        return s
    line = m.group(1)
    # compute indent from start of that line
    start = s.find(line)
    # backtrack to line start
    ls = s.rfind("\n", 0, start) + 1
    indent = s[ls:start]
    inj = f'{indent}self.btnBetCard.clicked.connect(self._open_bet_card)'
    # Insert after that line if not present
    after = start + len(line)
    return s[:after] + "\n" + inj + s[after:]

if not already_direct:
    src2 = insert_after_creation(src)
else:
    src2 = src

# 2) Add a late-scan safety (idempotent) at bottom of file
if "_patch_force_wire_bet_card" not in src2:
    safety = r
