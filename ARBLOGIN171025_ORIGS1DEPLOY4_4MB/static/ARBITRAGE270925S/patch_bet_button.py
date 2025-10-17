
import re, sys, os
from pathlib import Path

def die(msg):
    print("ERROR:", msg); sys.exit(1)

# Locate dashboard.py (current dir by default)
if len(sys.argv) > 1:
    root = Path(sys.argv[1])
else:
    root = Path(".")

dp = root / "dashboard.py"
if not dp.exists():
    die(f"dashboard.py not found in {root}")

src = dp.read_text(encoding="utf-8", errors="ignore")

# 1) Ensure QtCore alias and QTimer import
if "from PyQt6.QtCore import" in src and "QTimer" not in src:
    src = src.replace("from PyQt6.QtCore import Qt", "from PyQt6.QtCore import Qt, QTimer")
if "import PyQt6.QtCore as QtCore" not in src:
    # add after Qt import if present, else at top
    if "from PyQt6.QtCore import" in src:
        src = src.replace("from PyQt6.QtCore import Qt, QTimer", "from PyQt6.QtCore import Qt, QTimer\nimport PyQt6.QtCore as QtCore")
    else:
        src = "import PyQt6.QtCore as QtCore\n" + src

# 2) Inject guaranteed wiring after Clear button hookup
anchor = "self.btnClear.clicked.connect(self._clear_calc)"
inject = """
        # -- Bet Card button (guaranteed wiring) --
        try:
            if not hasattr(self, 'btnBetCard'):
                self.btnBetCard = QtWidgets.QPushButton("Bet Card")
            # reconnect safely
            try:
                try: self.btnBetCard.clicked.disconnect()
                except Exception: pass
                # status ping so you can see it fired
                try:
                    if callable(self.status_cb): self.btnBetCard.clicked.connect(lambda: self.status_cb("Bet Card (button)"))
                except Exception: pass
                self.btnBetCard.clicked.connect(self._open_bet_card)
            except Exception:
                self.btnBetCard.clicked.connect(self._open_bet_card)
            # place button in calculator UI if not already placed
            placed = False
            try:
                if 'rowBtns' in locals():
                    rowBtns.addWidget(self.btnBetCard); placed = True
            except Exception: pass
            if not placed:
                try:
                    if hasattr(self, 'calcBox') and self.calcBox.layout() is not None:
                        row = QtWidgets.QHBoxLayout(); row.addWidget(self.btnBetCard)
                        self.calcBox.layout().addLayout(row); placed = True
                except Exception: pass
            # initial enable state
            try:
                self.btnBetCard.setEnabled(bool(self.tblLive.selectedItems() or self.tblArb.selectedItems()))
            except Exception: pass
        except Exception: pass
"""
if anchor in src and "Bet Card button (guaranteed wiring)" not in src:
    src = src.replace(anchor, anchor + inject, 1)

# 3) Ensure selection change toggles enable state
src = src.replace(
    "tbl.itemSelectionChanged.connect(on_sel_changed)",
    "tbl.itemSelectionChanged.connect(on_sel_changed)\n                    try:\n                        if hasattr(self, 'btnBetCard'):\n                            self.btnBetCard.setEnabled(bool(tbl.selectedItems()))\n                    except Exception:\n                        pass"
)

dp.write_text(src, encoding="utf-8")
print("Patched:", dp.resolve())
