# start_dashboard.py — ARBITRAGE230925D
import os
os.environ["ARB_DISABLE_AUDIO"] = "1"
import dashboard as _dash

# Hard-disable any legacy audio methods if present
try:
    if hasattr(_dash, "Dashboard"):
        for fn in ("_play_ding", "_init_audio", "_ensure_ding_asset", "play_ding", "init_audio"):
            if hasattr(_dash.Dashboard, fn):
                setattr(_dash.Dashboard, fn, lambda self, *a, **k: None)
except Exception:
    pass

if hasattr(_dash, "main"):
    _dash.main()
else:
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    mw = getattr(_dash, "MainWindow", None)
    if mw:
        w = mw(); w.resize(1366, 820); w.show()
        sys.exit(app.exec())
