# patch_bet_button_G.py
import sys, re
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
DP   = ROOT / "dashboard.py"
src  = DP.read_text(encoding="utf-8", errors="ignore")

# Ensure QTimer + QtCore alias
if "from PyQt6.QtCore import" in src and "QTimer" not in src:
    src = src.replace("from PyQt6.QtCore import Qt", "from PyQt6.QtCore import Qt, QTimer")
if "import PyQt6.QtCore as QtCore" not in src:
    if "from PyQt6.QtCore import" in src:
        src = src.replace("from PyQt6.QtCore import Qt, QTimer",
                          "from PyQt6.QtCore import Qt, QTimer\nimport PyQt6.QtCore as QtCore")
    else:
        src = "from PyQt6.QtCore import QTimer\nimport PyQt6.QtCore as QtCore\n" + src

# Helper: target the Bet Card button specifically inside calcBox descendants
if "def _wire_bet_button_exact(" not in src:
    helper = r'''
    def _wire_bet_button_exact(self):
        """
        Force-wire the Bet Card button that lives under self.calcBox (calculator panel).
        Prefers an existing self.btnBetCard; otherwise finds a QPushButton in calcBox
        whose text contains 'bet' and 'card'. Connect both clicked & pressed.
        Adds a thin green outline and '(wired)' tooltip so we can confirm it.
        """
        try:
            from PyQt6 import QtWidgets
            # 1) Prefer attribute
            btn = getattr(self, "btnBetCard", None)
            # 2) If not set, search INSIDE calcBox only (avoid wiring other lookalikes)
            if btn is None and hasattr(self, "calcBox"):
                for w in self.calcBox.findChildren(QtWidgets.QPushButton):
                    t = (w.text() or "").lower()
                    n = (w.objectName() or "").lower()
                    if ("bet" in t and "card" in t) or ("bet" in n and "card" in n):
                        btn = w
                        break
            if btn is None:
                # last resort: global search
                for w in self.findChildren(QtWidgets.QPushButton):
                    t = (w.text() or "").lower()
                    n = (w.objectName() or "").lower()
                    if ("bet" in t and "card" in t) or ("bet" in n and "card" in n):
                        btn = w; break
            if btn is None:
                return
            # lock the attribute & name for future lookups
            self.btnBetCard = btn
            try:
                if not btn.objectName():
                    btn.setObjectName("betCardButton")
            except Exception:
                pass
            # disconnect any stale handlers
            try:
                try: btn.clicked.disconnect()
                except Exception: pass
                try: btn.pressed.disconnect()
                except Exception: pass
            except Exception:
                pass
            # status ping when it fires
            try:
                if callable(getattr(self, "status_cb", None)):
                    btn.clicked.connect(lambda: self.status_cb("Bet Card (button)"))
            except Exception:
                pass
            # connect both signals → extra safe
            try: btn.clicked.connect(self._open_bet_card)
            except Exception: pass
            try: btn.pressed.connect(self._open_bet_card)
            except Exception: pass
            # ensure enabled and visible
            try: btn.setEnabled(True)
            except Exception: pass
            try: btn.setVisible(True)
            except Exception: pass
            # raise visual confirmation
            try:
                ss = btn.styleSheet() or ""
                if "outline: 2px solid #3c3" not in ss:
                    btn.setStyleSheet(ss + " ; outline: 2px solid #3c3;")
                tip = (btn.toolTip() or "")
                if "(wired)" not in tip:
                    btn.setToolTip((tip + "  (wired)").strip())
            except Exception:
                pass
        except Exception as e:
            print("wire_bet_button_exact error", e)
    '''
    # insert before main()
    idx = src.rfind("def main(")
    src = (src + helper) if idx == -1 else (src[:idx] + helper + src[idx:])

# Schedule the wiring right after UI build (safe lambda)
init_idx = src.find("def __init__(self")
if init_idx != -1:
    nxt = src.find("\n    def ", init_idx+1)
    if nxt == -1: nxt = len(src)
    body = src[init_idx:nxt]
    if "self._build_ui()" in body and "_wire_bet_button_exact" not in body:
        body2 = body.replace(
            "self._build_ui()",
            "self._build_ui()\n        QTimer.singleShot(0, lambda: getattr(self, '_wire_bet_button_exact', lambda: None)())"
        )
        src = src[:init_idx] + body2 + src[nxt:]
    else:
        # make any existing singleShot call safe
        src = src.replace(
            "QTimer.singleShot(0, self._force_wire_bet_button)",
            "QTimer.singleShot(0, lambda: getattr(self, '_wire_bet_button_exact', lambda: None)())"
        )

DP.write_text(src, encoding="utf-8")
print("Patched G:", DP.resolve())
