import re, sys
from pathlib import Path
from PyQt6 import QtWidgets

def main(root: Path):
    dp = root / "dashboard.py"
    if not dp.exists():
        print("ERROR: dashboard.py not found in", root); sys.exit(1)
    src = dp.read_text(encoding="utf-8", errors="ignore")

    # Ensure imports
    if "from PyQt6.QtCore import" in src and "QTimer" not in src:
        src = src.replace("from PyQt6.QtCore import Qt",
                          "from PyQt6.QtCore import Qt, QTimer")
    if "import PyQt6.QtCore as QtCore" not in src:
        if "from PyQt6.QtCore import" in src:
            src = src.replace("from PyQt6.QtCore import Qt, QTimer",
                              "from PyQt6.QtCore import Qt, QTimer\nimport PyQt6.QtCore as QtCore")
        else:
            src = "from PyQt6.QtCore import QTimer\nimport PyQt6.QtCore as QtCore\n" + src

    # Add helper if missing
    if "def _force_wire_bet_button(" not in src:
        helper = '''
    def _force_wire_bet_button(self):
        """Late wiring: connect any Bet Card button to _open_bet_card"""
        try:
            btn = getattr(self, "btnBetCard", None)
            if btn is None:
                for w in self.findChildren(QtWidgets.QPushButton):
                    if "bet card" in w.text().lower():
                        btn = w; break
            if not btn: return
            self.btnBetCard = btn
            try:
                try: btn.clicked.disconnect()
                except Exception: pass
                if callable(self.status_cb):
                    btn.clicked.connect(lambda: self.status_cb("Bet Card (button)"))
                btn.clicked.connect(self._open_bet_card)
            except Exception:
                btn.clicked.connect(self._open_bet_card)
            try:
                btn.setEnabled(bool(self.tblLive.selectedItems() or self.tblArb.selectedItems()))
            except Exception: btn.setEnabled(True)
            # Outline so we know it wired
            ss = btn.styleSheet() or ""
            if "outline: 2px solid" not in ss:
                btn.setStyleSheet(ss + " ; outline: 2px solid #3c3;")
        except Exception as e:
            print("force_wire_bet_button error", e)
'''
        # Inject before main()
        idx = src.rfind("def main(")
        if idx == -1: src += helper
        else: src = src[:idx] + helper + src[idx:]

    # Call helper after build_ui
    init_idx = src.find("def __init__(self")
    if init_idx != -1:
        end = src.find("\n    def ", init_idx+1)
        if end == -1: end = len(src)
        body = src[init_idx:end]
        if "self._build_ui()" in body and "_force_wire_bet_button" not in body:
            body2 = body.replace("self._build_ui()",
                                 "self._build_ui()\n        QTimer.singleShot(0, self._force_wire_bet_button)")
            src = src[:init_idx] + body2 + src[end:]

    dp.write_text(src, encoding="utf-8")
    print("Patched (force):", dp.resolve())

if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    main(root)
