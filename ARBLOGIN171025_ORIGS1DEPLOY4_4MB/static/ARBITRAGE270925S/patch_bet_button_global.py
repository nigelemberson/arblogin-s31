# patch_bet_button_global.py
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
dp = root / "dashboard.py"
src = dp.read_text(encoding="utf-8", errors="ignore")

# Ensure QTimer import & QtCore alias
if "from PyQt6.QtCore import" in src and "QTimer" not in src:
    src = src.replace("from PyQt6.QtCore import Qt", "from PyQt6.QtCore import Qt, QTimer")
if "import PyQt6.QtCore as QtCore" not in src:
    if "from PyQt6.QtCore import" in src:
        src = src.replace("from PyQt6.QtCore import Qt, QTimer",
                          "from PyQt6.QtCore import Qt, QTimer\nimport PyQt6.QtCore as QtCore")
    else:
        src = "from PyQt6.QtCore import QTimer\nimport PyQt6.QtCore as QtCore\n" + src

helper = r'''
    def _scan_and_wire_bet_buttons(self):
        """Scan all QPushButtons; wire anything that looks like Bet Card. Idempotent."""
        try:
            from PyQt6 import QtWidgets
            cnt = 0
            for w in self.findChildren(QtWidgets.QPushButton):
                txt = (w.text() or "").lower()
                nm  = (w.objectName() or "").lower()
                if not (("bet" in txt and "card" in txt) or ("bet" in nm and "card" in nm)):
                    continue
                # skip if already tagged
                if getattr(w, "_betcard_wired", False):
                    continue
                # disconnect stale
                try: w.clicked.disconnect()
                except Exception: pass
                try: w.pressed.disconnect()
                except Exception: pass
                # status ping
                try:
                    if callable(getattr(self, "status_cb", None)):
                        w.clicked.connect(lambda: self.status_cb("Bet Card (button)"))
                except Exception: pass
                # connect both signals
                try: w.clicked.connect(self._open_bet_card)
                except Exception: pass
                try: w.pressed.connect(self._open_bet_card)
                except Exception: pass
                # make visible/enabled
                try: w.setEnabled(True); w.setVisible(True)
                except Exception: pass
                # visual cue + tag
                try:
                    ss = w.styleSheet() or ""
                    if "outline: 2px solid #3c3" not in ss:
                        w.setStyleSheet(ss + " ; outline: 2px solid #3c3;")
                    tip = (w.toolTip() or "")
                    if "(wired)" not in tip:
                        w.setToolTip((tip + "  (wired)").strip())
                    setattr(w, "_betcard_wired", True)
                except Exception: pass
                cnt += 1
            return cnt
        except Exception as e:
            print("scan_and_wire_bet_buttons error", e); return 0

    def _wire_bet_buttons_with_retries(self):
        """Retry wiring at 0ms, 500ms, 1000ms, 2000ms."""
        from PyQt6.QtCore import QTimer
        delays = [0, 500, 1000, 2000]
        def attempt(i=0):
            c = self._scan_and_wire_bet_buttons()
            try:
                if callable(getattr(self, "status_cb", None)):
                    self.status_cb(f"Wired {c} Bet Card button(s) [try {i+1}/{len(delays)}]")
            except Exception: pass
            if i+1 < len(delays):
                QTimer.singleShot(delays[i+1], lambda: attempt(i+1))
        attempt(0)
'''
if "_wire_bet_buttons_with_retries" not in src:
    idx = src.rfind("def main(")
    src = (src + helper) if idx == -1 else (src[:idx] + helper + src[idx:])

# Schedule after UI build
init_idx = src.find("def __init__(self")
if init_idx != -1:
    nxt = src.find("\n    def ", init_idx+1)
    if nxt == -1: nxt = len(src)
    body = src[init_idx:nxt]
    if "self._build_ui()" in body and "_wire_bet_buttons_with_retries" not in body:
        body2 = body.replace(
            "self._build_ui()",
            "self._build_ui()\n        QTimer.singleShot(0, lambda: getattr(self, '_wire_bet_buttons_with_retries', lambda: None)())"
        )
        src = src[:init_idx] + body2 + src[nxt:]

dp.write_text(src, encoding="utf-8")
print("Global bet-button wiring injected into:", dp.resolve())
