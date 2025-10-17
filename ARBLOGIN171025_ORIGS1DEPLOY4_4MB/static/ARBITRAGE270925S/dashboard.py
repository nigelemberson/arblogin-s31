
from PyQt6.QtCore import QObject, QEvent

class _SettingsBinder(QObject):
    # === Config & Threshold Wiring (existing keys; visual-only) ===
    def _app_dir(self):
        try:
            import __main__, os
            p = getattr(__main__, "__file__", None)
            if p:
                return os.path.abspath(os.path.dirname(p))
        except Exception:
            pass
        import os
        return os.getcwd()

    def _cfg_path(self):
        import os
        return os.path.join(self._app_dir(), "config.json")

    def load_config(self):
        import json, os
        try:
            p = self._cfg_path()
            if not os.path.exists(p):
                self.cfg = {"ding_edge_min": 3.0, "ding_profit_min": 10.0}
                self.save_config(self.cfg)
            else:
                with open(p, "r", encoding="utf-8") as f:
                    self.cfg = json.load(f) or {}
        except Exception:
            self.cfg = getattr(self, "cfg", {}) or {"ding_edge_min": 3.0, "ding_profit_min": 10.0}

    def save_config(self, cfg=None):
        import json
        try:
            p = self._cfg_path()
            data = cfg if cfg is not None else getattr(self, "cfg", {})
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _get_thresholds(self):
        try:
            if not hasattr(self, "cfg") or not isinstance(getattr(self, "cfg", None), dict):
                try: self.load_config()
                except Exception: self.cfg = {"ding_edge_min": 3.0, "ding_profit_min": 10.0}
            edge = self.cfg.get("ding_edge_min", getattr(self, "ding_edge_min", 3.0))
            profit = self.cfg.get("ding_profit_min", getattr(self, "ding_profit_min", 10.0))
            return float(edge), float(profit)
        except Exception:
            return 3.0, 10.0

    def _set_thresholds(self, edge=None, profit=None, persist=True):
        try:
            if not hasattr(self, "cfg") or not isinstance(getattr(self, "cfg", None), dict):
                try: self.load_config()
                except Exception: self.cfg = {"ding_edge_min": 3.0, "ding_profit_min": 10.0}
            if edge is not None:
                try:
                    edge = float(edge)
                    self.ding_edge_min = edge
                    self.cfg["ding_edge_min"] = edge
                except Exception:
                    pass
            if profit is not None:
                try:
                    profit = float(profit)
                    self.ding_profit_min = profit
                    self.cfg["ding_profit_min"] = profit
                except Exception:
                    pass
            if persist:
                try: self.save_config(self.cfg)
                except Exception: pass
            try: self._t2_eval_flash()
            except Exception: pass
        except Exception:
            pass

    def _bind_settings_fields(self, root=None):
        try:
            root = root or self
            edge_widgets = []
            profit_widgets = []
            # Search by known object names
            for name in ["spinEdge", "spinEdgeMin", "edgeSpin", "sbEdge", "edge_min", "Edge"]:
                try:
                    w = root.findChild((QDoubleSpinBox, QSpinBox), name)
                    if w and w not in edge_widgets:
                        edge_widgets.append(w)
                except Exception:
                    pass
            for name in ["spinProfit", "spinProfitMin", "profitSpin", "sbProfit", "profit_min", "Profit"]:
                try:
                    w = root.findChild((QDoubleSpinBox, QSpinBox), name)
                    if w and w not in profit_widgets:
                        profit_widgets.append(w)
                except Exception:
                    pass
            # If none found, scan form layouts by label text
            try:
                def collect_form_pairs(widget):
                    pairs = []
                    for form in widget.findChildren(QFormLayout):
                        try:
                            rows = form.rowCount()
                            for r in range(rows):
                                li = form.itemAt(r, QFormLayout.ItemRole.LabelRole)
                                fi = form.itemAt(r, QFormLayout.ItemRole.FieldRole)
                                lbl = li.widget() if li else None
                                fld = fi.widget() if fi else None
                                if isinstance(lbl, QLabel) and isinstance(fld, (QDoubleSpinBox, QSpinBox)):
                                    pairs.append((lbl.text().strip().lower(), fld))
                        except Exception:
                            pass
                    return pairs
                for text, fld in collect_form_pairs(root):
                    if "edge" in text and fld not in edge_widgets:
                        edge_widgets.append(fld)
                    if "profit" in text and fld not in profit_widgets:
                        profit_widgets.append(fld)
            except Exception:
                pass

            edge, profit = self._get_thresholds()
            for w in edge_widgets:
                try:
                    w.blockSignals(True); w.setValue(edge); w.blockSignals(False)
                except Exception:
                    pass
                try:
                    if not w.property("bound_edge"):
                        w.valueChanged.connect(lambda v, wref=w: self._set_thresholds(edge=v, profit=None, persist=True))
                        w.setProperty("bound_edge", True)
                except Exception:
                    pass
            for w in profit_widgets:
                try:
                    w.blockSignals(True); w.setValue(profit); w.blockSignals(False)
                except Exception:
                    pass
                try:
                    if not w.property("bound_profit"):
                        w.valueChanged.connect(lambda v, wref=w: self._set_thresholds(edge=None, profit=v, persist=True))
                        w.setProperty("bound_profit", True)
                except Exception:
                    pass

            # Hook OK/Apply/Save buttons if present
            for text in ["OK", "Ok", "Apply", "Save"]:
                try:
                    btns = [b for b in root.findChildren(QPushButton) if (b.text() or "").strip() == text]
                    for b in btns:
                        try: b.clicked.connect(lambda: self._set_thresholds(*self._get_thresholds(), persist=True))
                        except Exception: pass
                except Exception:
                    pass
        except Exception:
            pass

    def _scan_and_bind_threshold_spins(self):
        # Walk all top-level windows; bind any Edge/Profit controls we find
        try:
            app = QApplication.instance()
            if not app:
                return
            for w in app.topLevelWidgets():
                try:
                    self._bind_settings_fields(w)
                except Exception:
                    pass
        except Exception:
            pass

    # === Config & Threshold Wiring (keep existing keys) — visual-only, no audio ===
    def _app_dir(self):
        try:
            import __main__, os
            p = getattr(__main__, "__file__", None)
            if p:
                return os.path.abspath(os.path.dirname(p))
        except Exception:
            pass
        import os
        return os.getcwd()

    def _cfg_path(self):
        import os
        return os.path.join(self._app_dir(), "config.json")

    def load_config(self):
        import json
        try:
            with open(self._cfg_path(), "r", encoding="utf-8") as f:
                self.cfg = json.load(f) or {}
        except Exception:
            self.cfg = getattr(self, "cfg", {}) or {}

    def save_config(self, cfg=None):
        import json
        try:
            p = self._cfg_path()
            data = cfg if cfg is not None else getattr(self, "cfg", {})
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _get_thresholds(self):
        try:
            if not hasattr(self, "cfg") or not isinstance(getattr(self, "cfg", None), dict):
                try: self.load_config()
                except Exception: self.cfg = {}
            edge = self.cfg.get("ding_edge_min", getattr(self, "ding_edge_min", 3.0))
            profit = self.cfg.get("ding_profit_min", getattr(self, "ding_profit_min", 10.0))
            return float(edge), float(profit)
        except Exception:
            return 3.0, 10.0

    def _set_thresholds(self, edge=None, profit=None, persist=True):
        try:
            if not hasattr(self, "cfg") or not isinstance(getattr(self, "cfg", None), dict):
                try: self.load_config()
                except Exception: self.cfg = {}
            if edge is not None:
                try:
                    edge = float(edge)
                    self.ding_edge_min = edge
                    self.cfg["ding_edge_min"] = edge
                except Exception:
                    pass
            if profit is not None:
                try:
                    profit = float(profit)
                    self.ding_profit_min = profit
                    self.cfg["ding_profit_min"] = profit
                except Exception:
                    pass
            if persist:
                try: self.save_config(self.cfg)
                except Exception: pass
            try: self._t2_eval_flash()
            except Exception: pass
        except Exception:
            pass

    def _bind_settings_fields(self, dlg=None):
        try:
            from PyQt6.QtWidgets import QDialog, QDoubleSpinBox, QSpinBox, QPushButton, QLabel
            root = dlg or self
            # Try common names first
            edge_widgets = []
            profit_widgets = []
            for name in ["spinEdge", "spinEdgeMin", "edgeSpin", "sbEdge", "edge_min", "Edge"]:
                try:
                    w = root.findChild((QDoubleSpinBox, QSpinBox), name)
                    if w: edge_widgets.append(w)
                except Exception:
                    pass
            for name in ["spinProfit", "spinProfitMin", "profitSpin", "sbProfit", "profit_min", "Profit"]:
                try:
                    w = root.findChild((QDoubleSpinBox, QSpinBox), name)
                    if w: profit_widgets.append(w)
                except Exception:
                    pass

            # If not found by name, attempt label-based pairing for QFormLayout rows
            try:
                from PyQt6.QtWidgets import QFormLayout
                def collect_form_pairs(widget):
                    pairs = []
                    for form in widget.findChildren(QFormLayout):
                        try:
                            rows = form.rowCount()
                            for r in range(rows):
                                lbl_item = form.itemAt(r, QFormLayout.ItemRole.LabelRole)
                                fld_item = form.itemAt(r, QFormLayout.ItemRole.FieldRole)
                                lbl = lbl_item.widget() if lbl_item else None
                                fld = fld_item.widget() if fld_item else None
                                if isinstance(lbl, QLabel) and isinstance(fld, (QDoubleSpinBox, QSpinBox)):
                                    pairs.append((lbl.text().strip().lower(), fld))
                        except Exception:
                            pass
                    return pairs
                pairs = collect_form_pairs(root)
                for text, fld in pairs:
                    if ("edge" in text) and fld not in edge_widgets:
                        edge_widgets.append(fld)
                    if ("profit" in text) and fld not in profit_widgets:
                        profit_widgets.append(fld)
            except Exception:
                pass

            edge, profit = self._get_thresholds()
            for w in edge_widgets:
                try: w.setValue(edge)
                except Exception: pass
                try: w.valueChanged.connect(lambda v: self._set_thresholds(edge=v, profit=None, persist=True))
                except Exception: pass
            for w in profit_widgets:
                try: w.setValue(profit)
                except Exception: pass
                try: w.valueChanged.connect(lambda v: self._set_thresholds(edge=None, profit=v, persist=True))
                except Exception: pass

            # Hook OK/Apply/Save buttons if present to ensure persistence
            for text in ["OK", "Ok", "Apply", "Save"]:
                try:
                    btns = [b for b in root.findChildren(QPushButton) if (b.text() or "").strip() == text]
                    for b in btns:
                        try: b.clicked.connect(lambda: self._set_thresholds(*self._get_thresholds(), persist=True))
                        except Exception: pass
                except Exception:
                    pass
        except Exception:
            pass

    def __init__(self, owner):
        try: self.load_config()
        except Exception: pass
        try:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(800, self._scan_and_bind_threshold_spins)
            QTimer.singleShot(2000, self._scan_and_bind_threshold_spins)
            QTimer.singleShot(4000, self._scan_and_bind_threshold_spins)
            QTimer.singleShot(4500, self._t2_eval_flash)
        except Exception:
            pass

        try: self.load_config()
        except Exception: pass
        try:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app is not None and not hasattr(self, '_settings_binder'):
                self._settings_binder = _SettingsBinder(self)
                app.installEventFilter(self._settings_binder)
        except Exception:
            pass

        super().__init__(owner)
        self._owner = owner

    def eventFilter(self, obj, ev):
        try:
            if ev.type() == QEvent.Show and getattr(obj, "isWindow", lambda: False)():
                # Attempt to bind when any top-level dialog shows
                try: self._owner._bind_settings_fields(obj)
                except Exception: pass
        except Exception:
            pass
        return False
from alerts import Alerts
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QSlider, QPushButton, QGroupBox, QFormLayout, QDoubleSpinBox, QTabWidget, QTableWidgetItem
from PyQt6.QtWidgets import QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QSlider, QPushButton, QGroupBox, QFormLayout, QDoubleSpinBox
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QGroupBox, QFormLayout, QDoubleSpinBox
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtCore import QUrl, QTimer, Qt
import os as _os
__version__ = "ARBITRAGE270925S"
def _infer_mother_folder():
    try:
        _p = _os.path.abspath(__file__)
        return _os.path.basename(_os.path.dirname(_p))
    except Exception:
        try:
            return _os.path.basename(_os.getcwd())
        except Exception:
            return "UNKNOWN"
import os, sys
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt, QTimer
import PyQt6.QtCore as QtCore
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QFrame, QLabel, QSizePolicy,
    QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QTabWidget, QCheckBox, QMessageBox
)
from config_loader import load_config, save_config
from key_dialog import KeyDialog
from odds_feed import OddsFeed, OddsError

APP_TITLE = "SPORTS ARBITRAGE BOT — Dashboard (090925G14)"
ICON_PNG = os.path.join("assets", "icon.png")
ICON_ICO = os.path.join("assets", "icon.ico")

CLR_BG = "#121212"; CLR_PANEL = "#161616"; CLR_TEXT = "#ECECEC"
CLR_ORANGE_A = "#ff9830"; CLR_ORANGE_B = "#ff7a1a"; CLR_GREEN = "#20d070"

BTN_ORANGE = f"""
QPushButton {{
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {CLR_ORANGE_A}, stop:1 {CLR_ORANGE_B});
  color: #111;
  padding: 10px 16px;
  border-radius: 12px;
  border: 2px solid #d67415;
  border-top-color: #ffbe73;
  border-left-color: #ffbe73;
  font-weight: 800;
  font-size: 16px;
}}
QPushButton:pressed {{
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {CLR_ORANGE_B}, stop:1 #c7640f);
}}
"""

# Improve spinbox arrows
SPIN_QSS = f"""
QAbstractSpinBox {{
  background: #101010; color:{CLR_TEXT}; border:1px solid {CLR_GREEN}; border-radius:10px; padding:8px 36px;
}}
QAbstractSpinBox::up-button {{
  subcontrol-origin: border; subcontrol-position: top right; width:26px; height:16px;
  border-left:1px solid #2a2a2a; background:#0e0e0e; border-top-right-radius:10px;
}}
QAbstractSpinBox::down-button {{
  subcontrol-origin: border; subcontrol-position: bottom right; width:26px; height:16px;
  border-left:1px solid #2a2a2a; background:#0e0e0e; border-bottom-right-radius:10px;
}}
QAbstractSpinBox::up-button:hover, QAbstractSpinBox::down-button:hover {{ background:#1c1c1c; }}
QAbstractSpinBox::up-arrow, QAbstractSpinBox::down-arrow {{
  width: 10px; height:10px;
}}
"""
# QSS for the green "League" capsule (header)
PANEL_BORDER = f"border:2px solid {CLR_GREEN}; border-radius:12px; background:{CLR_PANEL};"
HEADER_STYLE = f"""
QHeaderView::section {{
  padding: 8px 12px;
  font-weight: 800;
  font-size: 16px;
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {CLR_ORANGE_A}, stop:1 {CLR_ORANGE_B});
  color: #111;
  border: 1px solid #000;
}}
"""
TABLE_STYLE = f"""
QTableWidget {{
  gridline-color: #3c3c3c;
  background: {CLR_BG};
  color: {CLR_TEXT};
  selection-background-color: #242424;
  selection-color: #ffffff;
  border: 1px solid #000;
  font-size: 16px;
}}
QTableWidget::item {{ padding: 6px 10px; }}
QScrollBar:vertical {{
  background:#0f0f0f; width:12px; margin:0;
}}
QScrollBar::handle:vertical {{ background:#303030; min-height:20px; border-radius:4px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
QScrollBar:horizontal {{ background:#0f0f0f; height:12px; margin:0; }}
QScrollBar::handle:horizontal {{ background:#303030; min-width:20px; border-radius:4px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width:0; }}
"""

def _ensure_spin_icons():
    """Create +/− PNGs and return absolute forward-slash paths."""
    try:
        import os
        from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor
        from PyQt6.QtCore import Qt
        base = os.path.dirname(__file__); assets = os.path.join(base, "assets")
        os.makedirs(assets, exist_ok=True)
        plus  = os.path.join(assets, "spin_plus.png")
        minus = os.path.join(assets, "spin_minus.png")
        def make(ch, path):
            pm = QPixmap(18, 18); pm.fill(Qt.GlobalColor.transparent)
            p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setBrush(QColor("#ff8c2a")); p.setPen(QColor("#ff8c2a"))
            p.drawRoundedRect(0, 0, 17, 17, 6, 6)
            p.setPen(QColor("#111")); f = QFont(); f.setPointSize(12); f.setBold(True); p.setFont(f)
            p.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, ch); p.end()
            pm.save(path, "PNG")
        if not os.path.exists(plus):  make("+", plus)
        if not os.path.exists(minus): make("−", minus)
        return plus.replace("\\","/"), minus.replace("\\","/")
    except Exception:
        return None, None
APP_QSS = f"""
QMainWindow {{ background: {CLR_BG}; }}
QWidget {{ color: {CLR_TEXT}; }}
QTabWidget::pane {{ border:1px solid {CLR_GREEN}; background:{CLR_BG}; }}
QTabBar::tab {{
  background:{CLR_PANEL}; color:{CLR_TEXT}; padding:6px 12px;
  border:1px solid {CLR_GREEN}; border-bottom:none; border-top-left-radius:6px; border-top-right-radius:6px;
  margin-right:2px;
}}
QTabBar::tab:selected {{ background:#1b1b1b; }}
{SPIN_QSS}
QComboBox {{
  background: #101010; color:{CLR_TEXT}; border:1px solid {CLR_GREEN}; border-radius:10px; padding:8px 12px;
}}
QComboBox QAbstractItemView {{
  background:#101010; color:{CLR_TEXT}; border:1px solid {CLR_GREEN};
  selection-background-color:#333; selection-color:#fff;
}}
"""

class Dashboard(QWidget):
    # === Threshold wiring (keep existing keys) — in-code, visual-only ===
    def _get_thresholds(self):
        try:
            edge = float(getattr(self, 'ding_edge_min', float(getattr(self, 'cfg', {}).get('ding_edge_min', 3.0))))
        except Exception:
            edge = 3.0
        try:
            profit = float(getattr(self, 'ding_profit_min', float(getattr(self, 'cfg', {}).get('ding_profit_min', 10.0))))
        except Exception:
            profit = 10.0
        return edge, profit

    def _set_thresholds(self, edge=None, profit=None, persist=True):
        try:
            if edge is not None:
                try: edge = float(edge)
                except Exception: edge = None
            if profit is not None:
                try: profit = float(profit)
                except Exception: profit = None
            if edge is not None:
                self.ding_edge_min = edge
                try: self.cfg['ding_edge_min'] = edge
                except Exception: pass
            if profit is not None:
                self.ding_profit_min = profit
                try: self.cfg['ding_profit_min'] = profit
                except Exception: pass
            if persist:
                try:
                    if hasattr(self, 'save_config') and callable(self.save_config):
                        self.save_config(self.cfg)
                except Exception: pass
            try: self._t2_eval_flash()
            except Exception: pass
        except Exception:
            pass

    def _bind_settings_fields(self, dlg=None):
        try:
            from PyQt6.QtWidgets import QDoubleSpinBox, QSpinBox, QPushButton
            root = dlg or self
            edge_widgets = []
            profit_widgets = []
            for name in ["spinEdge", "spinEdgeMin", "edgeSpin", "sbEdge", "edge_min", "Edge"]:
                w = root.findChild((QDoubleSpinBox, QSpinBox), name)
                if w: edge_widgets.append(w)
            for name in ["spinProfit", "spinProfitMin", "profitSpin", "sbProfit", "profit_min", "Profit"]:
                w = root.findChild((QDoubleSpinBox, QSpinBox), name)
                if w: profit_widgets.append(w)
            edge, profit = self._get_thresholds()
            for w in edge_widgets:
                try: w.setValue(edge)
                except Exception: pass
                try: w.valueChanged.connect(lambda v: self._set_thresholds(edge=v, profit=None, persist=False))
                except Exception: pass
            for w in profit_widgets:
                try: w.setValue(profit)
                except Exception: pass
                try: w.valueChanged.connect(lambda v: self._set_thresholds(edge=None, profit=v, persist=False))
                except Exception: pass
            for text in ["OK", "Ok", "Apply", "Save"]:
                try:
                    btns = [b for b in root.findChildren(QPushButton) if (b.text() or "").strip() == text]
                    for b in btns:
                        try: b.clicked.connect(lambda: self._set_thresholds(*self._get_thresholds(), persist=True))
                        except Exception: pass
                except Exception: pass
        except Exception:
            pass

    # === T2 Flashing (visual only; OR logic) ===
    def _t2_init_flasher(self):
        from PyQt6.QtCore import QTimer
        from PyQt6.QtGui import QColor
        self._t2_flash_timer = QTimer(self)
        self._t2_flash_timer.setInterval(500)
        self._t2_flash_timer.timeout.connect(self._t2_apply_flash_tick)
        self._t2_flash_on = False
        self._t2_flash_rows = {}  # row -> reason ("edge"|"profit"|"both")
        self._t2_prev_bg = {}     # (row,col) -> QBrush to restore
        self._t2_color_edge = QColor(0, 200, 0, 140)
        self._t2_color_profit = QColor(255, 215, 0, 160)
        self._t2_color_both = QColor(220, 20, 60, 160)
        try: self._t2_flash_timer.start()
        except Exception: pass

    def _t2_clear_flash_state(self):
        try:
            tbl = getattr(self, "tblArb", None) or getattr(self, "table2", None)
            if tbl is None:
                self._t2_prev_bg = {}; self._t2_flash_rows = {}
                return
            from PyQt6.QtGui import QColor
            for (r,c), prev in list(getattr(self, "_t2_prev_bg", {}).items()):
                try:
                    it = tbl.item(r, c)
                    if it:
                        if prev is None:
                            it.setBackground(QColor(0,0,0,0))
                        else:
                            it.setBackground(prev)
                except Exception: pass
            self._t2_prev_bg = {}; self._t2_flash_rows = {}
            try: tbl.viewport().update()
            except Exception: pass
        except Exception: pass
    def _t2_eval_flash(self):
        edge_thresh, profit_thresh = self._get_thresholds()
        tbl = getattr(self, "tblArb", None) or getattr(self, "table2", None)
        if tbl is None:
            return
        edge_thresh, profit_thresh = self._get_thresholds()
    
        edge_col = profit_col = None
        try:
            headers = [ (tbl.horizontalHeaderItem(i).text() if tbl.horizontalHeaderItem(i) else "") for i in range(tbl.columnCount()) ]
            for i, name in enumerate(headers):
                nn = (name or "").strip().lower()
                nn = nn.replace("%"," percent ").replace("£"," gbp ").replace("$"," usd ").replace("€"," eur ")
                if edge_col is None and ("edge" in nn):
                    edge_col = i
                if profit_col is None and ("profit" in nn or "gbp" in nn or "profit (" in nn):
                    profit_col = i
        except Exception:
            pass
        if edge_col is None or profit_col is None:
            return
    
        new_rows = {}
        try:
            for r in range(tbl.rowCount()):
                # Edge value
                try:
                    it_e = tbl.item(r, edge_col)
                    se = (it_e.text() if it_e else "").strip()
                    for ch in ["%", ",", "£", "$", "€"]:
                        se = se.replace(ch, "")
                    e = float(se) if se else 0.0
                except Exception:
                    e = 0.0
                # Profit value
                try:
                    it_p = tbl.item(r, profit_col)
                    sp = (it_p.text() if it_p else "").strip()
                    for ch in ["%", ",", "£", "$", "€"]:
                        sp = sp.replace(ch, "")
                    p = float(sp) if sp else 0.0
                except Exception:
                    p = 0.0
    
                reason = None
                if e >= edge_thresh and p >= profit_thresh:
                    reason = "both"
                elif e >= edge_thresh:
                    reason = "edge"
                elif p >= profit_thresh:
                    reason = "profit"
                if reason:
                    new_rows[r] = reason
        except Exception:
            pass
    
        self._t2_flash_rows = new_rows


    def _t2_apply_flash_tick(self):
        from PyQt6.QtGui import QColor
        tbl = getattr(self, "tblArb", None) or getattr(self, "table2", None)
        if tbl is None: return
        self._t2_flash_on = not getattr(self, "_t2_flash_on", False)
        for r, reason in list(getattr(self, "_t2_flash_rows", {}).items()):
            for c in range(tbl.columnCount()):
                it = tbl.item(r, c)
                if not it: continue
                key = (r,c)
                if key not in self._t2_prev_bg:
                    try: self._t2_prev_bg[key] = it.background()
                    except Exception: self._t2_prev_bg[key] = None
                try:
                    if self._t2_flash_on:
                        if reason == "both": it.setBackground(self._t2_color_both)
                        elif reason == "edge": it.setBackground(self._t2_color_edge)
                        elif reason == "profit": it.setBackground(self._t2_color_profit)
                    else:
                        if self._t2_prev_bg.get(key) is None:
                            it.setBackground(QColor(0,0,0,0))
                        else:
                            it.setBackground(self._t2_prev_bg.get(key))
                except Exception: pass
        try: tbl.viewport().update()
        except Exception: pass
        for key in list(self._t2_prev_bg.keys()):
            r,c = key
            if r not in getattr(self, "_t2_flash_rows", {}):
                self._t2_prev_bg.pop(key, None)

    # === Demo/Live toggle and unified fetch wrapper ===
    def _toggle_demo_mode(self, checked: bool):
        self._demo_mode = bool(checked)
        label = "Demo:  ON" if self._demo_mode else "Demo: OFF"
        try:
            self.btnDemo.setText(label)
            self.btnDemo.setStyleSheet("color:#16a34a;" if self._demo_mode else "color:#ef4444;")
        except Exception:
            pass
        try:
            self.status_cb("Demo mode ON (dummy data)" if self._demo_mode else "Demo mode OFF (live API)")
        except Exception:
            pass


    def _fetch_once_wrapper(self):
        try:
            if getattr(self, "_demo_mode", False):
                self._fetch_once_demo()
            else:
                # Call the app's real single-fetch method
                self._fetch_now()
        except Exception as e:
            try: self.status_cb(f"Fetch error: {e}")
            except Exception: pass

    def _fetch_once_demo(self):
        from PyQt6.QtWidgets import QTableWidgetItem
        tbl_live = getattr(self, "tblLive", None)
        tbl_arb  = getattr(self, "tblArb",  None) or getattr(self, "table2", None)

        demo_live_cols = ["Sport","League","Match","Book","Price","Time"]
        demo_live_rows = [
            {"Sport":"Football","League":"EPL","Match":"Arsenal vs Spurs","Book":"Bet365","Price":"2.10","Time":"12:30"},
            {"Sport":"Football","League":"EPL","Match":"Chelsea vs Brighton","Book":"Pinnacle","Price":"1.95","Time":"14:00"},
            {"Sport":"Tennis","League":"ATP","Match":"Player A vs B","Book":"Smarkets","Price":"1.72","Time":"16:15"},
        ]

        demo_arb_cols = ["Bookmaker","Outcome","Back Odds","Lay Odds","Edge %","Stake","Profit"]
        demo_arb_rows = [
            {"Bookmaker":"Betfair","Outcome":"Home","Back Odds":"2.04","Lay Odds":"2.00","Edge %":"5.2","Stake":"100","Profit":"£ 12.50"},
            {"Bookmaker":"Bet365","Outcome":"Away","Back Odds":"2.55","Lay Odds":"2.50","Edge %":"3.0","Stake":"80","Profit":"£ 0.80"},
            {"Bookmaker":"Pinnacle","Outcome":"Draw","Back Odds":"3.30","Lay Odds":"3.25","Edge %":"0.1","Stake":"100","Profit":"£ 5.00"},
        ]

        if tbl_live is not None:
            tbl_live.setColumnCount(len(demo_live_cols))
            tbl_live.setHorizontalHeaderLabels(demo_live_cols)
            tbl_live.setRowCount(0)
            for r in demo_live_rows:
                rr = tbl_live.rowCount(); tbl_live.insertRow(rr)
                for c, key in enumerate(demo_live_cols):
                    tbl_live.setItem(rr, c, QTableWidgetItem(str(r.get(key,""))))

        if tbl_arb is not None:
            tbl_arb.setColumnCount(len(demo_arb_cols))
            tbl_arb.setHorizontalHeaderLabels(demo_arb_cols)
            tbl_arb.setRowCount(0)
            for r in demo_arb_rows:
                rr = tbl_arb.rowCount(); tbl_arb.insertRow(rr)
                for c, key in enumerate(demo_arb_cols):
                    tbl_arb.setItem(rr, c, QTableWidgetItem(str(r.get(key,""))))
            try: self._t2_eval_flash()
            except Exception: pass

        try: self.status_cb("Demo data loaded.")
        except Exception: pass
        try:
            if not hasattr(self, '_t2_flash_timer'):
                self._t2_init_flasher()
        except Exception:
            pass
    # === T2 Flashing (OR logic) ===
    def _t2_init_flasher(self):
        from PyQt6.QtCore import QTimer
        from PyQt6.QtGui import QColor
        self._t2_flash_timer = QTimer(self)
        self._t2_flash_timer.setInterval(500)  # 2 Hz toggle
        self._t2_flash_timer.timeout.connect(self._t2_apply_flash_tick)
        self._t2_flash_on = False
        self._t2_flash_rows = {}  # row -> reason ("edge"|"profit"|"both")
        self._t2_prev_bg = {}     # (row,col) -> QBrush to restore
        self._t2_color_edge = QColor(0, 200, 0, 140)
        self._t2_color_profit = QColor(255, 215, 0, 160)
        self._t2_color_both = QColor(220, 20, 60, 160)
        try:
            self._t2_flash_timer.start()
        except Exception:
            pass
    def _t2_eval_flash(self):
        edge_thresh, profit_thresh = self._get_thresholds()
        tbl = getattr(self, "tblArb", None) or getattr(self, "table2", None)
        if tbl is None:
            return
        edge_thresh, profit_thresh = self._get_thresholds()
    
        edge_col = profit_col = None
        try:
            headers = [ (tbl.horizontalHeaderItem(i).text() if tbl.horizontalHeaderItem(i) else "") for i in range(tbl.columnCount()) ]
            for i, name in enumerate(headers):
                nn = (name or "").strip().lower()
                nn = nn.replace("%"," percent ").replace("£"," gbp ").replace("$"," usd ").replace("€"," eur ")
                if edge_col is None and ("edge" in nn):
                    edge_col = i
                if profit_col is None and ("profit" in nn or "gbp" in nn or "profit (" in nn):
                    profit_col = i
        except Exception:
            pass
        if edge_col is None or profit_col is None:
            return
    
        new_rows = {}
        try:
            for r in range(tbl.rowCount()):
                # Edge value
                try:
                    it_e = tbl.item(r, edge_col)
                    se = (it_e.text() if it_e else "").strip()
                    for ch in ["%", ",", "£", "$", "€"]:
                        se = se.replace(ch, "")
                    e = float(se) if se else 0.0
                except Exception:
                    e = 0.0
                # Profit value
                try:
                    it_p = tbl.item(r, profit_col)
                    sp = (it_p.text() if it_p else "").strip()
                    for ch in ["%", ",", "£", "$", "€"]:
                        sp = sp.replace(ch, "")
                    p = float(sp) if sp else 0.0
                except Exception:
                    p = 0.0
    
                reason = None
                if e >= edge_thresh and p >= profit_thresh:
                    reason = "both"
                elif e >= edge_thresh:
                    reason = "edge"
                elif p >= profit_thresh:
                    reason = "profit"
                if reason:
                    new_rows[r] = reason
        except Exception:
            pass
    
        self._t2_flash_rows = new_rows


    def _t2_apply_flash_tick(self):
        tbl = getattr(self, "tblArb", None) or getattr(self, "table2", None)
        if tbl is None: return
        self._t2_flash_on = not getattr(self, "_t2_flash_on", False)
        on = self._t2_flash_on
        try:
            self._t2_eval_flash()
        except Exception:
            pass
        from PyQt6.QtGui import QBrush, QColor
        rows = tbl.rowCount(); cols = tbl.columnCount()
        for r in range(rows):
            reason = self._t2_flash_rows.get(r)
            for c in range(cols):
                it = tbl.item(r, c)
                if not it: continue
                key = (r,c)
                if on and reason:
                    if key not in self._t2_prev_bg:
                        try: self._t2_prev_bg[key] = it.background()
                        except Exception: self._t2_prev_bg[key] = None
                    if reason == "edge":   br = QBrush(self._t2_color_edge)
                    elif reason == "profit": br = QBrush(self._t2_color_profit)
                    else:                  br = QBrush(self._t2_color_both)
                    try:
                        it.setBackground(br)
                        it.setData(Qt.BackgroundRole, br)
                    except Exception: pass
                else:
                    if key in self._t2_prev_bg:
                        try:
                            prev = self._t2_prev_bg.get(key)
                            if prev is None: it.setBackground(QColor(0,0,0,0))
                            else: it.setBackground(prev)
                        except Exception: pass
        try:
            tbl.viewport().update()
        except Exception:
            pass
        for key in list(self._t2_prev_bg.keys()):
            r,c = key
            if r not in self._t2_flash_rows:
                self._t2_prev_bg.pop(key, None)

    def _t2_clear_flash(self):
        tbl = getattr(self, "tblArb", None) or getattr(self, "table2", None)
        if tbl is None: return
        from PyQt6.QtGui import QColor
        rows = tbl.rowCount(); cols = tbl.columnCount()
        for r in range(rows):
            for c in range(cols):
                it = tbl.item(r, c)
                if it:
                    try: it.setBackground(QColor(0,0,0,0))
                    except Exception: pass
        self._t2_prev_bg = {}
        self._t2_flash_rows = {}
        self._t2_flash_on = False
    def _play_ding(self):
        """No-op in audio-purged build."""
        try:
            return
        except Exception:
            return

    def _play_ding(self):
        """No-op in audio-purged build."""
        try:
            return
        except Exception:
            return

    def _apply_selection_style(self):
        try:
            from PyQt6.QtWidgets import QAbstractItemView
            names = ['tableLive','tableArbs','tblLive','tblArbs','tblArb']
            for name in names:
                tv = getattr(self, name, None)
                if tv is None:
                    continue
                try:
                    tv.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
                    tv.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
                    ss = tv.styleSheet() or ''
                    if 'QTableView::item:selected' not in ss:
                        ss += '\nQTableView::item:selected { background-color: #1a3; color: white; }\n'
                    tv.setStyleSheet(ss)
                except Exception:
                    pass
        except Exception:
            pass

    # --- logout styling helpers ---
    def _show_logout_dialog(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QApplication
        from PyQt6.QtCore import Qt
        dlg = QDialog(self); dlg.setWindowTitle("Logout"); dlg.setModal(True)
        dlg.setStyleSheet("""
            QDialog { background: #0f0f0f; color: #e5e7eb; border: 1px solid #222; border-radius: 12px; }
            QLabel { color: #e5e7eb; font-size: 14px; }
            QPushButton { background: #ff8c2a; color: #111; border: none; padding: 6px 14px; border-radius: 10px; font-weight: 600; }
            QPushButton:hover { /* filter removed */ }
            QPushButton:disabled { background: #2a2a2a; color: #777; }
        """)
        v = QtWidgets.QVBoxLayout(dlg); v.setContentsMargins(16,16,16,16); v.setSpacing(14)
        v.addWidget(QLabel("Exit the application?"), alignment=Qt.AlignmentFlag.AlignLeft)
        row = QtWidgets.QHBoxLayout(); row.addStretch(1)
        y = QPushButton("Yes", dlg); n = QPushButton("No", dlg)
        row.addWidget(y); row.addWidget(n); v.addLayout(row)
        decided = {"yes": False}
        y.clicked.connect(lambda: (decided.update(yes=True), dlg.accept()))
        n.clicked.connect(dlg.reject)
        n.setAutoDefault(True); n.setDefault(True)
        # removed wrong size for Bet Card; dlg.exec()
        if decided["yes"]:
            QApplication.quit()

    def _patch_logout_button(self):
        try:
            from PyQt6.QtWidgets import QPushButton
            for b in self.findChildren(QPushButton):
                if (b.text() or "").strip().lower() == "logout":
                    try: b.clicked.disconnect()
                    except Exception: pass
                    b.clicked.connect(self._show_logout_dialog)
                    break
        except Exception:
            pass
    # --- end logout helpers ---

    # === UI toggle styling (added) ===
    def _wire_toggle_styles(self):
        try:
            from PyQt6.QtWidgets import QPushButton, QSpinBox, QDoubleSpinBox
        except Exception:
            return

        auto_refresh_btn = None
        auto_fetch_btn = None

        for b in self.findChildren(QPushButton):
            t = (b.text() or "").strip().lower()
            if "auto refresh" in t and auto_refresh_btn is None:
                auto_refresh_btn = b
            elif ("fetch auto api" in t or "auto fetch" in t) and auto_fetch_btn is None:
                auto_fetch_btn = b

        # Fetch-every spinbox, often named spnSecs
        spn = getattr(self, "spnSecs", None)
        if spn is None:
            for c in self.findChildren((QSpinBox, QDoubleSpinBox)):
                name = (c.objectName() or "").lower()
                if "sec" in name or "fetch" in name:
                    spn = c
                    break

        def style_btn(b, bg, fg):
            try: b.setStyleSheet(f"background:{bg}; color:{fg}; border:none;")
            except Exception: pass

        # Match fonts with a reference top-row button (Fetch One API or Refresh Odds / Arbs)
        try:
            ref_btn = None
            for b in self.findChildren(QPushButton):
                t = (b.text() or "").strip().lower()
                if "fetch one api" in t or "refresh odds" in t:
                    ref_btn = b; break
            if ref_btn:
                rf = ref_btn.font()
                if auto_refresh_btn: auto_refresh_btn.setFont(rf)
                if auto_fetch_btn:   auto_fetch_btn.setFont(rf)
        except Exception:
            pass

        # Button 4 — Auto Refresh: OFF=orange, ON=green; text flips
        if auto_refresh_btn:
            try: auto_refresh_btn.setCheckable(True)
            except Exception: pass
            def _style_auto(on, b=auto_refresh_btn):
                try:
                    b.setText("Auto Refresh: On" if on else "Auto Refresh: Off")
                    if on: style_btn(b, "#20d070", "#111")
                    else:  style_btn(b, "#ff7a1a", "#111")
                except Exception: pass
            _style_auto(auto_refresh_btn.isChecked())
            try: auto_refresh_btn.toggled.disconnect()
            except Exception: pass
            auto_refresh_btn.toggled.connect(lambda on, b=auto_refresh_btn: _style_auto(on, b))

        # Button 3 — Fetch Auto API: OFF=red, ON=green; disables spinbox while ON
        if auto_fetch_btn:
            try: auto_fetch_btn.setCheckable(True)
            except Exception: pass
            try: auto_fetch_btn.setChecked(False)   # start OFF (red)
            except Exception: pass
            def _style_fetch(on, b=auto_fetch_btn):
                try:
                    if on: style_btn(b, "#20d070", "#111")
                    else:  style_btn(b, "#b71c1c", "#111")
                    if spn: spn.setEnabled(not on)
                except Exception: pass
            _style_fetch(auto_fetch_btn.isChecked())
            try: auto_fetch_btn.toggled.disconnect()
            except Exception: pass
            auto_fetch_btn.toggled.connect(lambda on, b=auto_fetch_btn: _style_fetch(on, b))
    # === end toggle styling ===

    # No-op styling hook to avoid QObject init errors if called before super().__init__()
    def _beautify_spinboxes(self):
        return
    def __init__(self, parent=None, status_cb=None):
        try: self._t2_init_flasher()
        except Exception: pass
        try: self._bind_settings_fields(None)
        except Exception: pass

        self.alerts = Alerts(enabled=False)
        super().__init__(parent)
        self.status_cb = status_cb or (lambda s: None)
        self.cfg = load_config()
        plus_img, minus_img = _ensure_spin_icons()
        # load persisted flags/thresholds
        try:
            self.ding_enabled = bool(self.cfg.get('ding_enabled', True))
        except Exception:
            self.ding_enabled = True
        try:
            self.ding_volume = float(self.cfg.get('ding_volume', 70))
        except Exception:
            self.ding_volume = 70
        try:
            self.ding_edge_min = float(self.cfg.get('ding_edge_min', 3.0))
            self.ding_profit_min = float(self.cfg.get('ding_profit_min', 10.0))
        except Exception:
            self.ding_edge_min = 3.0; self.ding_profit_min = 10.0
        self.sanity_check_enabled = bool(self.cfg.get('sanity_check_enabled', True))
        self._api_key = self.cfg.get("odds_api_key","")
        self._auto_copy = bool(self.cfg.get("auto_copy", False))
        self.feed = OddsFeed(lambda: self._api_key)
        self.auto_timer = QTimer(self); self.auto_timer.timeout.connect(self._fetch_once_wrapper)
        abs_plus = (plus_img or os.path.join(os.path.dirname(__file__), 'assets', 'spin_plus.png')).replace('\\','/')
        abs_minus = (minus_img or os.path.join(os.path.dirname(__file__), 'assets', 'spin_minus.png')).replace('\\','/')
        spin_img_qss = f"QAbstractSpinBox::up-button {{ subcontrol-origin: padding; subcontrol-position: top right; width:22px; height:18px; margin:0; }} " \
                        f"QAbstractSpinBox::down-button {{ subcontrol-origin: padding; subcontrol-position: bottom right; width:22px; height:18px; margin:0; }} " \
                        f"QAbstractSpinBox::up-arrow {{ image: url('{abs_plus}'); width:16px; height:16px; }} " \
                        f"QAbstractSpinBox::down-arrow {{ image: url('{abs_minus}'); width:16px; height:16px; }} "
        self.setStyleSheet(APP_QSS + "\n" + spin_img_qss)
        self._build_ui()
        # --- Flashing thresholds ---
        self.flash_min_edge = 70.0  # percent threshold for Edge %
        self.flash_min_profit = 1.0  # absolute profit threshold
        self._arbFlashOn = False
        try:
            from PyQt6 import QtCore
            self._arbFlashTimer = QtCore.QTimer(self)
            self._arbFlashTimer.setInterval(500)
            self._arbFlashTimer.timeout.connect(self._tick_arb_flash)
            self._arbFlashTimer.start()
        except Exception:
            pass

        # FORCE_SPINBOX_ARROWS
        try:
            from PyQt6.QtWidgets import QAbstractSpinBox
            for sp in (getattr(self,'spnSecs',None), getattr(self,'inStake',None), getattr(self,'inA',None), getattr(self,'inB',None), getattr(self,'inComm',None), getattr(self,'inFee',None)):
                if sp is not None:
                    sp.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        except Exception:
            pass

        try:
            wav = self._ensure_ding_asset() if hasattr(self, "_ensure_ding_asset") else None
            if wav:
                                from PyQt6.QtCore import QUrl
            else:
                pass
        except Exception:
            pass
        # --- Ding sound setup ---
        try:
            wav = os.path.join(os.path.dirname(__file__), "assets", "ding.wav")
            self._ding.setSource(QUrl.fromLocalFile(wav))
            self._ding.setVolume(float(self.cfg.get("ding_volume", 0.6)))
        except Exception:
            pass
        QTimer.singleShot(0, lambda: getattr(self, '_wire_bet_buttons_with_retries', lambda: None)())
        QTimer.singleShot(0, lambda: getattr(self, '_wire_calcbox_bet_button_with_retries', lambda: None)())
        QTimer.singleShot(0, lambda: getattr(self, '_wire_bet_button_exact', lambda: None)())
        QTimer.singleShot(0, lambda: getattr(self, '_force_wire_bet_button', lambda: None)())
        self._apply_selection_style()
        try:
            self._wire_toggle_styles()
        except Exception:
            pass
        try:
            pass  # inserted after removal of logout
        except Exception:
            pass

        # ensure Logout is wired (v2)
        try:
            pass  # inserted after removal of logout
        except Exception:
            pass
        # schedule once after show
        try:
            import PyQt6.QtCore as _QtCore
        except Exception:
            pass

        self._fill_demo_data()

    def _build_ui(self):
        self.grid = QtWidgets.QGridLayout(self)
        self.grid.setContentsMargins(12,8,12,10)
        self.grid.setHorizontalSpacing(12); self.grid.setVerticalSpacing(10)

        self.titleBox = QFrame(objectName="titleBox"); self.titleBox.setStyleSheet(PANEL_BORDER)
        layT = QtWidgets.QHBoxLayout(self.titleBox); layT.setContentsMargins(16,8,16,8); layT.setSpacing(12)
        self.logo = QLabel()
        icon_path = ICON_ICO if os.path.exists(ICON_ICO) else None
        if icon_path:
            pm = QtGui.QPixmap(icon_path)
            if not pm.isNull():
                self.logo.setPixmap(pm.scaled(44,44, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                self.logo.setFixedSize(48,48)
                layT.addWidget(self.logo, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.brand = QLabel("SPORTS ARBITRAGE BOT"); self.brand.setStyleSheet("font-size:40px; font-weight:900; letter-spacing:1px;")
        layT.addWidget(self.brand, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter);

        # --- Clean header controls (no extra frames) ---
        # Fetch every
        labFetch = QLabel("Fetch every"); labFetch.setStyleSheet("font-weight:800; font-size:18px;")
        self.spnSecs = QDoubleSpinBox(); self.spnSecs.setDecimals(0); self.spnSecs.setRange(0, 3600); self.spnSecs.setSingleStep(10); self.spnSecs.setValue(0)
        self.spnSecs.setFixedHeight(34); self.spnSecs.setMinimumWidth(140)
        self.spnSecs.setMaximumWidth(200)
        layT.addWidget(labFetch, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        layT.addWidget(self.spnSecs, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        # League
        lab = QLabel("League"); lab.setStyleSheet("font-weight:800; font-size:18px;")
        self.cmbLeague = QComboBox(); self.cmbLeague.addItems(["EPL","MLS","A-League","J1 League","K League","India (ISL)","IPL"])
        self.cmbLeague.setFixedHeight(34); self.cmbLeague.setMinimumWidth(160)
        self.cmbLeague.setMaximumWidth(200)
        self.cmbLeague.setStyleSheet("""
QComboBox { font-size: 18px; padding-top: 2px; padding-bottom: 2px; padding-left: 8px; padding-right: 26px; }
QComboBox QAbstractItemView { font-size: 18px; }
QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 22px; border: 0px; margin-right: 4px; }
""" )
        layT.addWidget(lab, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        layT.addWidget(self.cmbLeague, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        layT.addStretch(1)
        self.controlsBox = QFrame(objectName="controlsBox"); self.controlsBox.setStyleSheet(PANEL_BORDER)
        v = QtWidgets.QVBoxLayout(self.controlsBox); v.setContentsMargins(16,12,16,12); v.setSpacing(10)
        cap = QLabel("Controls"); cap.setStyleSheet("font-weight:800; font-size:18px;"); v.addWidget(cap)
        def add_btn(text):
            from PyQt6.QtWidgets import QSizePolicy
            b = QPushButton(text)
            b.setStyleSheet(BTN_ORANGE)
            b.setMinimumHeight(46)
            try:
                b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            except Exception:
                pass
            v.addWidget(b)
            return b
        self.btnRefresh   = add_btn("Refresh Odds / Arbs")
        self.btnFetchNow  = add_btn("Fetch One API")
        self.btnAutoFetch = add_btn("Fetch Auto API")
        # Demo toggle
        self._demo_mode = False
        self.btnDemo = QPushButton('Demo: OFF', self)
        # (270925S) Fix Demo width and policy so toggling never changes header size
        try:
            from PyQt6.QtWidgets import QSizePolicy
            fm = self.fontMetrics()
            _dw = max(fm.horizontalAdvance('Demo: OFF'), fm.horizontalAdvance('Demo:  ON')) + 16
            self.btnDemo.setFixedWidth(_dw)
            self.btnDemo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.btnDemo.setStyleSheet('color:#ef4444;')
        except Exception:
            pass
        self.btnDemo.setCheckable(True)
        self.btnDemo.clicked.connect(self._toggle_demo_mode)
        layT.addWidget(self.btnDemo, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        # Red theme for API buttons (fetch-one and fetch-auto)
        try:
            self.btnFetchNow.setStyleSheet(
                BTN_ORANGE + """
QPushButton { background:#b71c1c; border-color:#ff5b5b; }
QPushButton:hover { background:#c62828; }
QPushButton:pressed { background:#a01515; }
""")
            self.btnAutoFetch.setStyleSheet(
                BTN_ORANGE + """
QPushButton { background:#b71c1c; border-color:#ff5b5b; }
QPushButton:hover { background:#c62828; }
QPushButton:pressed { background:#a01515; }
""")
        except Exception:
            pass

        self.btnAutoRefresh = add_btn("Auto Refresh: Off")
        self.btnExport = add_btn("Export")
        self.btnSettings = add_btn("Settings"); self.btnAudit = add_btn("Audit Log")
        self.btnExit = add_btn("Exit")
        v.addStretch(1)

        # wire control buttons
        # ensure Key button exists and is wired
        try:
            self.btnKey
        except Exception:
            try:
                self.btnKey = add_btn("Key...")
            except Exception:
                pass
        try:
            self.btnKey.clicked.disconnect()
        except Exception:
            pass
        self.btnKey.clicked.connect(self._open_key_dialog)

        # --- Robust Exit wiring (inline, independent of class method) ---
        from PyQt6 import QtWidgets as _QtW
        def _exit_now():
            from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
            try:
                from exit_dialog_custom import ExitDialog
                body_font = getattr(self, 'tblFeed', self).font()
                accent = self._accent_green_hex_from_table() if hasattr(self,'_accent_green_hex_from_table') else '#1aff97'
                dlg = ExitDialog(self, accent_color=accent, body_font=body_font)
                res = dlg.exec()
                if res == QDialog.DialogCode.Accepted:
                    QApplication.instance().quit()
            except Exception:
                r = QMessageBox.question(self, 'Confirm Exit', 'Exit the application?')
                if r == QMessageBox.StandardButton.Yes:
                    QApplication.instance().quit()
        try:
            self.btnExit.clicked.disconnect()
        except Exception:
            pass
        self.btnExit.clicked.connect(_exit_now)

        # Safe dynamic wiring
        # (skips missing/late-created widgets)
        try:
            pairs = [
                ('btnRefresh', '_refresh_odds_arbs'),
                ('btnExport', '_export_csv'),
                ('btnSettings', '_open_settings'),
                ('btnAudit', '_open_audit_log'),
                ('btnLogout', '_logout'),
                ('btnAutoRefresh', '_toggle_ui_refresh'),
                ('btnLive', '_toggle_live_minute'),
                ('btnBetCard', '_open_bet_card'),
                ('btnCalc', '_calculate'),
                ('btnClear', '_clear_calc'),
                ('btnUseSel', '_use_selection')
            ]
            for name, handler in pairs:
                btn = getattr(self, name, None)
                fn  = getattr(self, handler, None)
                if btn and callable(fn):
                    btn.clicked.connect(fn)
        except Exception:
            pass
        if hasattr(self, 'btnAutoCopy'):
            try:
                self.btnAutoCopy.toggled.connect(self._toggle_auto_copy)
            except Exception:
                pass

        self.btnFetchNow.clicked.connect(self._fetch_once_wrapper)
        self.btnAutoFetch.clicked.connect(self._toggle_auto_fetch)

        self.centerBox = QFrame(objectName="centerBox"); self.centerBox.setStyleSheet(PANEL_BORDER)
        vc = QtWidgets.QVBoxLayout(self.centerBox); vc.setContentsMargins(14,10,14,10); vc.setSpacing(8)

        headerRow = QtWidgets.QHBoxLayout(); headerRow.setContentsMargins(0,0,0,0)
        cap1 = QLabel("Table 1: Live Feed"); cap1.setStyleSheet("font-weight:800; font-size:18px;")
        headerRow.addWidget(cap1, 0, Qt.AlignmentFlag.AlignLeft)
        headerRow.addStretch(1)
        self.btnQuota = QPushButton("Quota: demo"); self.btnQuota.setStyleSheet("QPushButton{background:#0f0f0f;color:#cfead9;padding:6px 10px;border-radius:14px;border:2px solid %s;font-weight:800;font-size:13px;}" % CLR_GREEN); self.btnQuota.setFixedHeight(28)
        try:
            try:
                try:
                    self.btnQuota.clicked.disconnect()
                except Exception:
                    pass
            except Exception:
                pass
        except Exception:
            pass
        self.btnQuota.clicked.connect(self._show_quota_details)
        headerRow.addWidget(self.btnQuota, 0, Qt.AlignmentFlag.AlignRight)
        vc.addLayout(headerRow)

        self.tblLive = QTableWidget( 0, 6); self.tblLive.setHorizontalHeaderLabels(["Sport","League","Match","Book","Price","Time"]); vc.addWidget(self.tblLive)
        self.tblLive.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tblLive.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tblLive.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.lblReload1 = QLabel("Last reload: demo"); self.lblReload1.setStyleSheet("color:#9fd; font-size:16px;"); vc.addWidget(self.lblReload1)

        cap2 = QLabel("Table 2: Arbitrage Opportunities"); cap2.setStyleSheet("font-weight:800; font-size:18px;"); vc.addWidget(cap2)
        self.tblArb = QTableWidget(0, 7); self.tblArb.setHorizontalHeaderLabels(["Bookmaker","Outcome","Back Odds","Lay Odds","Edge %","Stake","Profit"]); vc.addWidget(self.tblArb)

        # --- Ensure Table 2 sizing: Bookmaker stretches; numerics compact; Profit visible ---
        try:
            _hdr2 = self.tblArb.horizontalHeader()
            from PyQt6.QtWidgets import QHeaderView as _QHV
            _hdr2.setStretchLastSection(False)
            labels = ["Bookmaker","Outcome","Back Odds","Lay Odds","Edge %","Stake","Profit"]
            for i,name in enumerate(labels):
                if name == "Bookmaker":
                    _hdr2.setSectionResizeMode(i, _QHV.ResizeMode.Stretch)
                else:
                    _hdr2.setSectionResizeMode(i, _QHV.ResizeMode.ResizeToContents)
            def _clamp(i, lo, hi):
                try:
                    self.tblArb.resizeColumnToContents(i)
                    w = self.tblArb.columnWidth(i)
                    if w < lo: self.tblArb.setColumnWidth(i, lo)
                    elif w > hi: self.tblArb.setColumnWidth(i, hi)
                except Exception:
                    pass
            _clamp(0, 140, 700)
            _clamp(1,  80, 140)
            _clamp(2,  70, 120)
            _clamp(3,  70, 120)
            _clamp(4,  80, 130)
            _clamp(5,  90, 150)
            _clamp(6, 100, 170)
        except Exception:
            pass
        self.tblArb.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tblArb.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tblArb.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.lblReload2 = QLabel("Last reload: demo"); self.lblReload2.setStyleSheet("color:#9fd; font-size:16px;"); vc.addWidget(self.lblReload2)

        self.calcBox = QFrame(objectName="calcBox"); self.calcBox.setStyleSheet(PANEL_BORDER)
        vx = QtWidgets.QVBoxLayout(self.calcBox); vx.setContentsMargins(16,12,16,12); vx.setSpacing(10)
        cap3 = QLabel("Table 3: Calculator — Inputs"); cap3.setStyleSheet("font-weight:800; font-size:18px;"); vx.addWidget(cap3)

        g = QtWidgets.QGridLayout(); g.setHorizontalSpacing(8); g.setVerticalSpacing(6)
        def lab(s): l=QLabel(s); l.setStyleSheet("font-weight:700;"); return l
        self.inStake = QDoubleSpinBox(); self.inStake.setRange(0,1_000_000); self.inStake.setValue(100.0)
        self.inA = QDoubleSpinBox(); self.inA.setDecimals(3); self.inA.setRange(1.0,1000.0); self.inA.setValue(2.100)
        self.inB = QDoubleSpinBox(); self.inB.setDecimals(3); self.inB.setRange(1.0,1000.0); self.inB.setValue(3.600)
        self.inComm = QDoubleSpinBox(); self.inComm.setDecimals(2); self.inComm.setSuffix(" %"); self.inComm.setRange(0,100); self.inComm.setValue(0.00)
        self.inFee = QDoubleSpinBox(); self.inFee.setDecimals(2); self.inFee.setRange(0,10_000); self.inFee.setValue(0.00)

        # --- Normalize spinbox font sizes to match Table 1 appearance ---
        try:
            from PyQt6.QtGui import QFont as _QFont
            _spin_font = _QFont(); _spin_font.setPointSize(12); _spin_font.setBold(False)
            _spin_font_bold = _QFont(); _spin_font_bold.setPointSize(12); _spin_font_bold.setBold(True)
            # Calculator spinboxes
            self.inStake.setFont(_spin_font_bold)   # bold for comparison
            self.inA.setFont(_spin_font_bold)       # bold for comparison
            self.inB.setFont(_spin_font)
            self.inComm.setFont(_spin_font)
            self.inFee.setFont(_spin_font)
            # Controls: Fetch Every
            self.spnSecs.setFont(_spin_font)
        except Exception as _e:
            pass
        g.addWidget(lab("Total Stake"),0,0); g.addWidget(self.inStake,0,1)
        g.addWidget(lab("Odds A"),1,0); g.addWidget(self.inA,1,1)
        g.addWidget(lab("Odds B"),2,0); g.addWidget(self.inB,2,1)
        g.addWidget(lab("Commission %"),3,0); g.addWidget(self.inComm,3,1)
        g.addWidget(lab("Fixed Fee"),4,0); g.addWidget(self.inFee,4,1)
        vx.addLayout(g)

        r1 = QtWidgets.QHBoxLayout(); r2 = QtWidgets.QHBoxLayout()
        def add_btn_calc(text):
            b = QPushButton(text); b.setStyleSheet(BTN_ORANGE); b.setMinimumHeight(46); b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed); return b
        self.btnCalc = add_btn_calc("Calculate"); self.btnClear = add_btn_calc("Clear")
        r1.addWidget(self.btnCalc); r1.addWidget(self.btnClear); vx.addLayout(r1)
        self.btnUseSel = add_btn_calc("Use Selection"); r2.addWidget(self.btnUseSel)
        self.btnAutoCopy = add_btn_calc("Auto Copy"); self.btnAutoCopy.setCheckable(True); self.btnAutoCopy.setChecked(self._auto_copy)
        self.btnAutoCopy.setStyleSheet(BTN_ORANGE + "\nQPushButton:checked { background:#cc6a1a; border-color:#ff9a3a; }\nQPushButton:checked:hover { background:#d87422; }")
        r2.addWidget(self.btnAutoCopy); vx.addLayout(r2)
        self.btnBetCard = add_btn_calc("Bet Card"); vx.addWidget(self.btnBetCard)

        self.btnBetCard.clicked.connect(self._open_bet_card)

        outCap = QLabel("Outputs"); outCap.setStyleSheet("font-weight:800; font-size:18px;"); vx.addWidget(outCap)
        self.outputs = QFrame(); self.outputs.setStyleSheet("QFrame{border:1px solid #000;border-radius:8px; background:#0f0f0f;}")
        ov = QtWidgets.QGridLayout(self.outputs); ov.setContentsMargins(10,8,10,8); ov.setHorizontalSpacing(8); ov.setVerticalSpacing(6)
        def add_out(r, label):
            lab = QLabel(label); lab.setWordWrap(False); lab.setMinimumWidth(160); lab.setStyleSheet("font-weight:700; padding-right:6px;"); val = QLineEdit(); val.setReadOnly(True); val.setMinimumHeight(34)
            val.setStyleSheet("QLineEdit{background:#101010;color:#ECECEC;border:1px solid #2a2a2a;border-radius:8px;padding:6px 8px;}")
            ov.addWidget(lab, r, 0); ov.addWidget(val, r, 1); return val
        self.outStakeA = add_out(0,"Stake A"); self.outStakeB = add_out(1,"Stake B"); self.outEdge = add_out(2,"Edge %")
        self.outPA = add_out(3,"Profit if A wins"); self.outPB = add_out(4,"Profit if B wins"); self.outMin = add_out(5,"Min Profit")
        vx.addWidget(self.outputs,1)
        # --- Ensure output value fonts match inputs (12pt, normal) ---
        try:
            from PyQt6.QtGui import QFont as _QFont
            _o_font = _QFont(); _o_font.setPointSize(12); _o_font.setBold(False)
            for _w in (self.outStakeA, self.outStakeB, self.outEdge, self.outPA, self.outPB, self.outMin):
                try:
                    _w.setFont(_o_font)
                except Exception:
                    pass
        except Exception:
            pass

        # wire calc buttons
        self.btnAutoCopy.toggled.connect(self._toggle_auto_copy)
        self.btnCalc.clicked.connect(self._calculate)
        self.btnClear.clicked.connect(self._clear_calc)

        self.btnUseSel.clicked.connect(self._use_selection)
        # --- Remember which table had the last user selection & keep selections mutually exclusive ---
        try:
            self._last_selected_table = None
            def _wire_sel(tbl, name):
                try:
                    def on_sel_changed():
                        # Remember where the human last clicked
                        self._last_selected_table = name
                        # keep selections mutually exclusive to avoid stale hits
                        other = self.tblArb if tbl is self.tblLive else self.tblLive
                        try:
                            if other.selectionModel():
                                other.selectionModel().clearSelection()
                        except Exception:
                            try: other.clearSelection()
                            except Exception: pass
                    tbl.itemSelectionChanged.connect(on_sel_changed)
                    on_sel_changed()
                    try:
                        if hasattr(self, 'btnBetCard'):
                            self.btnBetCard.setEnabled(bool(tbl.selectedItems()))
                    except Exception:
                        pass
                except Exception:
                    pass
            _wire_sel(self.tblLive, "live")
            _wire_sel(self.tblArb,  "arb")
        except Exception:
            pass

        # polish tables
        for tbl in (self.tblLive, self.tblArb):
            tbl.setStyleSheet(TABLE_STYLE + HEADER_STYLE)
            tbl.verticalHeader().setVisible(False)
            tbl.verticalHeader().setDefaultSectionSize(32)
            hh: QHeaderView = tbl.horizontalHeader()
            from PyQt6.QtWidgets import QHeaderView as _QHV
            if tbl is self.tblLive:
                hh.setStretchLastSection(True)
                hh.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                hh.setSectionResizeMode(_QHV.ResizeMode.Stretch)
            else:
                hh.setStretchLastSection(False)
                hh.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            tbl.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
            tbl.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
            tbl.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
            try:
                from PyQt6.QtCore import QTimer
                tbl.itemDoubleClicked.connect(lambda *args, **kw: QTimer.singleShot(150, lambda: self._open_bet_card(show_empty_warning=False)))
            except Exception:
                pass
        # Apply selection highlight styling to both tables
        try:
            self._apply_selection_style()
        except Exception:
            pass

        # Layout grid
        self.grid.addWidget(self.titleBox,0,0,1,2)
        self.grid.addWidget(self.calcBox,0,2,2,1)
        self.grid.addWidget(self.controlsBox,1,0,1,1)
        self.grid.addWidget(self.centerBox,1,1,1,1)
        self.grid.setColumnStretch(0,1); self.grid.setColumnStretch(1,3); self.grid.setColumnStretch(2,1)
        self.grid.setRowStretch(1,1)
        # -- Keyboard shortcut: Ctrl+B to open Bet Card --
        try:
            from PyQt6.QtGui import QShortcut, QKeySequence
            self._shortcut_betcard = QShortcut(QKeySequence("Ctrl+B"), self)
            self._shortcut_betcard.activated.connect(self._open_bet_card)
        except Exception:
            pass

        # === Final bind: ensure the orange Bet Card button is wired (release) ===
        try:
            if hasattr(self, "btnBetCard") and self.btnBetCard is not None:
                try:
                    self.btnBetCard.clicked.disconnect()
                except Exception:
                    pass
                self.btnBetCard.clicked.connect(self._open_bet_card)
                try:
                    self.btnBetCard.setEnabled(True)
                except Exception:
                    pass
        except Exception:
            pass
        # === End final bind ===

    def _fetch_now(self):
        # --- Cooldown / reentrancy guard (3 seconds) ---
        import time
        if getattr(self, "_fetching", False):
            try:
                if callable(self.status_cb): self.status_cb("Fetch ignored: already running.")
            except Exception: pass
            return
        now = time.time()
        last = getattr(self, "_last_fetch_ts", 0.0)
        if (now - last) < 3.0:
            try:
                if callable(self.status_cb): self.status_cb(f"Fetch ignored: clicked too quickly ({now - last:.1f}s).")
            except Exception: pass
            return
        self._last_fetch_ts = now
        self._fetching = True
        try:
            if hasattr(self, "btnFetchNow"): self.btnFetchNow.setEnabled(False)
            if hasattr(self, "btnRefresh"):  self.btnRefresh.setEnabled(False)
        except Exception:
            pass
        league = self.cmbLeague.currentText()
        try:
            rows, quota = self.feed.fetch_live(league)
            self._populate_table(self.tblLive, rows, ["Sport","League","Match","Book","Price","Time"])
            self._update_quota(quota or {})
            quota_txt = ", ".join(f"{k}:{v}" for k,v in (quota or {}).items()) or "—"
            self.lblReload1.setText(f"Last reload (API): ok  |  {quota_txt}")
            self.status_cb("API fetch ok")
        except OddsError as e:
            QMessageBox.warning(self, "Fetch error", str(e))
            self.status_cb("API fetch error")
        except Exception as e:
            QMessageBox.critical(self, "Unexpected error", str(e))
            self.status_cb("API fetch exception")
        # -- finally: re-enable --
        self._fetching = False
        try:
            if hasattr(self, "btnFetchNow"): self.btnFetchNow.setEnabled(True)
            if hasattr(self, "btnRefresh"):  self.btnRefresh.setEnabled(True)
        except Exception:
            pass

    def _toggle_auto_fetch(self):
        if hasattr(self, 'auto_timer') and self.auto_timer.isActive():
            self.auto_timer.stop()
            self.btnAutoFetch.setText("Fetch Auto API: Off"); self.spnSecs.setEnabled(True)
            self.status_cb("Auto Fetch stopped")
        else:
            if not hasattr(self, 'auto_timer'):
                self.auto_timer = QTimer(self); self.auto_timer.timeout.connect(self._fetch_once_wrapper)
            interval_ms = int(self.spnSecs.value()) * 1000
            self.auto_timer.start(interval_ms)
            self.btnAutoFetch.setText("Fetch Auto API: On"); self.spnSecs.setEnabled(False)
            self.status_cb(f"Auto Fetch every {int(self.spnSecs.value())}s")

    def _populate_table(self, tbl: QTableWidget, rows, cols):
        tbl.setRowCount(0)
        for r in rows:
            rr = tbl.rowCount(); tbl.insertRow(rr)
            for c, key in enumerate(cols):
                tbl.setItem(rr, c, QTableWidgetItem(str(r.get(key, ""))))
        try:
            if tbl is getattr(self, 'tblArb', None) or tbl is getattr(self, 'table2', None):
                self._t2_eval_flash()
        except Exception:
            pass

    def _toggle_auto_copy(self, checked: bool):
        self._auto_copy = bool(checked); self.cfg["auto_copy"] = self._auto_copy; save_config(self.cfg)

    def _calculate(self):
        S = float(self.inStake.value())
        a = float(self.inA.value()); b = float(self.inB.value())
        fee = float(self.inFee.value()); comm = float(self.inComm.value())/100.0
        if a <= 1.0 or b <= 1.0 or S <= 0:
            for w in (self.outStakeA, self.outStakeB, self.outEdge, self.outPA, self.outPB, self.outMin):
                w.setText(""); return
        stakeA = S * b / (a + b); stakeB = S * a / (a + b)
        retA = stakeA * a * (1.0 - comm); retB = stakeB * b * (1.0 - comm)
        profitA = retA - S - fee; profitB = retB - S - fee
        edge_pct = (min(profitA, profitB) / S) * 100.0
        self.outStakeA.setText(f"{stakeA:,.0f}"); self.outStakeB.setText(f"{stakeB:,.2f}")
        self.outEdge.setText(f"{edge_pct:,.2f} %"); self.outPA.setText(f"$ {profitA:,.2f}")
        self.outPB.setText(f"$ {profitB:,.0f}"); self.outMin.setText(f"$ {min(profitA, profitB):,.2f}")

    def _clear_calc(self):
        for w in (self.outStakeA, self.outStakeB, self.outEdge, self.outPA, self.outPB, self.outMin):
            w.setText("")

    def _use_selection(self):
        """Routes selection from whichever table the user actually interacted with last.

        Rules:
            pass
        1) If a table has focus and a valid selection, use that.
        2) Else if _last_selected_table is set, use that table if selection is valid.
        3) Else fall back to 'arb' then 'live' with validity checks.
        """
        try:
            from PyQt6.QtWidgets import QApplication
        except Exception:
            QApplication = None

        def grab_from_live():
            try:
                r = self.tblLive.currentRow()
                if r is None or r < 0: return False
                price_item = self.tblLive.item(r,4)
                if price_item is None: return False
                price = float(price_item.text())
                self.inA.setValue(price)
                return True
            except Exception:
                return False

        def grab_from_arb():
            try:
                r = self.tblArb.currentRow()
                if r is None or r < 0: return False
                b = self.tblArb.item(r,2); l = self.tblArb.item(r,3)
                if b is None: return False
                back_odds = float(b.text())
                self.inA.setValue(back_odds)
                if l is not None:
                    try:
                        lay_odds = float(l.text())
                        if lay_odds > 0: self.inB.setValue(lay_odds)
                    except Exception:
                        pass
                return True
            except Exception:
                return False

        # 1) Focus preference
        try:
            if getattr(self.tblLive, 'hasFocus', lambda: False)() and self.tblLive.selectedItems():
                if grab_from_live():
                    self._calculate();
                    return
            if getattr(self.tblArb, 'hasFocus', lambda: False)() and self.tblArb.selectedItems():
                if grab_from_arb():
                    self._calculate();
                    return
        except Exception:
            pass

        # 2) Recency preference
        if getattr(self, "_last_selected_table", None) == "live" and self.tblLive.selectedItems():
            if grab_from_live():
                self._calculate();
                return
        if getattr(self, "_last_selected_table", None) == "arb" and self.tblArb.selectedItems():
            if grab_from_arb():
                self._calculate();
                return

        # 3) Fallback
        if self.tblArb.selectedItems():
            if grab_from_arb():
                self._calculate();
                return
        if self.tblLive.selectedItems():
            if grab_from_live():
                self._calculate();
                return

        # If nothing worked, show a gentle status (when available)
        try:
            if callable(self.status_cb):
                self.status_cb("No row selected. Click a row in Table 1 or Table 2 first.")
        except Exception:
            pass

    def _open_key_dialog(self):
        def get_text(): return self._api_key or ""
        def set_text(s: str):
            self._api_key = s or ""
            cfg = load_config(); cfg["odds_api_key"] = self._api_key; save_config(cfg); self.cfg = cfg
        KeyDialog.show_singleton(self, get_text, set_text)

    def _fill_demo_data(self):
        rows,_ = self.feed.fetch_demo()
        self._populate_table(self.tblLive, rows, ["Sport","League","Match","Book","Price","Time"])
        self.lblReload1.setText("Last reload: demo"); self._update_quota({"source":"demo"})

        demo_arb=[("Betfair","—","10.5","0","80.5","0"),
                  ("Smarkets","—","8.0","0","75.0","0"),
                  ("Unibet (NL)","—","5.75","0","65.1","0")]
        self.tblArb.setRowCount(0)
        for row in demo_arb*10:
            rr=self.tblArb.rowCount(); self.tblArb.insertRow(rr)
            for c,val in enumerate(row):
                self.tblArb.setItem(rr, c, QTableWidgetItem(str(val)))
        self.lblReload2.setText("Last reload: demo")

    # --- Quota helpers ---
    def _update_quota(self, quota: dict):
        used = None; remaining = None; limit = None; last = None
        lines = []
        for k,v in (quota or {}).items():
            kl = k.lower()
            if "used" in kl: used = v
            if "remaining" in kl: remaining = v
            if "limit" in kl or "quota" in kl: limit = v
            if "last" in kl: last = v
            lines.append(f"{k}: {v}")
        if quota.get("source") == "demo":
            self.btnQuota.setText("Quota: demo")
            self.btnQuota.setToolTip("")
        else:
            if used is not None and (limit is not None or remaining is not None):
                _second = last if last is not None else (limit if limit is not None else '?')
                label = f"Quota: {used}/{_second}"
                if remaining is not None: label += f" • {remaining} left"
                self.btnQuota.setText(label)
            elif remaining is not None:
                self.btnQuota.setText(f"Quota: {remaining} left")
            else:
                self.btnQuota.setText("Quota: —")
            self.btnQuota.setToolTip("")
    def _show_quota_details(self):
        QtWidgets.QMessageBox.information(self, "API Quota", self.btnQuota.toolTip() or "No quota information.")

    # === Added: full handlers so every button works ===
    def _refresh_odds_arbs(self):
        """UI-only refresh: repaint tables and post bottom status.
        Do NOT touch the green API band; only update Table 2 label with timestamp."""
        try:
            # Repaint existing tables only
            if hasattr(self, 'tblLive') and self.tblLive:
                self.tblLive.viewport().update()
            if hasattr(self, 'tblArb') and self.tblArb:
                self.tblArb.viewport().update()
            # Update only the Table 2 label with timestamp
            try:
                from datetime import datetime
                ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if hasattr(self, 'lblReload2') and self.lblReload2:
                    self.lblReload2.setText(f'Last refresh (UI): {ts}')
            except Exception:
                pass
            # Bottom status message
            try:
                if callable(self.status_cb):
                    self.status_cb('Refresh complete (UI only)')
            except Exception:
                pass
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, 'Refresh', f'Failed: {e}')
    def _toggle_ui_refresh(self):
        import PyQt6.QtCore as _QtCore
        def tick():
            try:
                if hasattr(self, "tblLive") and self.tblLive: self.tblLive.viewport().update()
                if hasattr(self, "tblArb") and self.tblArb:   self.tblArb.viewport().update()
            except Exception: pass
        if not hasattr(self, "ui_refresh_timer"):
            self.ui_refresh_timer = QTimer(self); self.ui_refresh_timer.setInterval(1000); self.ui_refresh_timer.timeout.connect(tick)
        if self.ui_refresh_timer.isActive():
            self.ui_refresh_timer.stop()
            try: self.btnAutoRefresh.setText("Auto Refresh: Off")
            except Exception: pass
            if callable(self.status_cb): self.status_cb("UI Auto Refresh OFF")
        else:
            self.ui_refresh_timer.start()
            try: self.btnAutoRefresh.setText("Auto Refresh: On")
            except Exception: pass
            if callable(self.status_cb): self.status_cb("UI Auto Refresh ON")

    def _open_bet_card(self, show_empty_warning: bool = True):
        try:
            if callable(self.status_cb): self.status_cb('Opening Bet Card...')
        except Exception:
            pass
        """
        Open a Bet Card dialog populated from the currently selected row
        (either Table 1 Live or Table 2 Arbs). Also saves bet_card.txt at the app root.
        """
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton, QMessageBox, QApplication
        from PyQt6.QtCore import Qt
        import os, datetime

        # Helper to read cells safely
        def cell(tbl, r, c):
            try:
                it = tbl.item(r, c)
                return it.text() if it else ""
            except Exception:
                return ""

        # Determine which table to read from (reuse the same routing rules as _use_selection)
        src = None
        # Prefer focus table if selection present
        row = -1
        if getattr(self.tblLive, 'hasFocus', lambda: False)() and self.tblLive.selectedItems():
            src = 'live'; row = self.tblLive.currentRow()
        elif getattr(self.tblArb, 'hasFocus', lambda: False)() and self.tblArb.selectedItems():
            src = 'arb'; row = self.tblArb.currentRow()
        elif getattr(self, "_last_selected_table", None) == "live" and self.tblLive.selectedItems():
            src = "live"; row = self.tblLive.currentRow()
        elif getattr(self, "_last_selected_table", None) == "arb" and self.tblArb.selectedItems():
            src = "arb"; row = self.tblArb.currentRow()
        elif self.tblArb.selectedItems():
            src = "arb"; row = self.tblArb.currentRow()
        elif self.tblLive.selectedItems():
            src = "live"; row = self.tblLive.currentRow()

        if src is None or row is None or row < 0:

            if show_empty_warning:
                QMessageBox.information(self, "Bet Card", "Select a row in Table 1 or Table 2 first.")
            return
            return

        # Extract fields
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mother = _infer_mother_folder()

        if src == "live":
            # Table 1 columns: League, Match, Book, Price, Time (based on your build)
            league = cell(self.tblLive, row, 0)
            match  = cell(self.tblLive, row, 1)
            book   = cell(self.tblLive, row, 2)
            price  = cell(self.tblLive, row, 4)
            when   = cell(self.tblLive, row, 5)
            card_title = f"BET CARD — Live (Table 1) — {mother}"
            body = [
                f"Timestamp: {now_str}",
                f"League:    {league}",
                f"Match:     {match}",
                f"Book:      {book}",
                f"Price:     {price}",
                f"Time:      {when}",
                "",
                f"Notes: Copy to clipboard to place bet."
            ]
        else:
            # Table 2 columns: Book Odds, Lay Odds, Edge %, Stake — but your header shows more;
            # We'll read conservatively.
            # Safer approach: show entire row values with headers when present.
            headers = []
            vals = []
            try:
                hc = self.tblArb.columnCount()
                for c in range(hc):
                    h = self.tblArb.horizontalHeaderItem(c)
                    headers.append(h.text() if h else f"Col{c}")
                    vals.append(cell(self.tblArb, row, c))
            except Exception:
                pass
            card_title = f"BET CARD — Arbitrage (Table 2) — {mother}"
            body = [f"Timestamp: {now_str}"]
            for h,v in zip(headers, vals):
                body.append(f"{h}: {v}")
            body.append("")
            body.append("Notes: Copy to clipboard to place bet.")

        content = "\n".join(body)

        # Save to bet_card.txt at app root
        try:
            root = os.path.dirname(__file__)
            out = os.path.join(root, "bet_card.txt")
            with open(out, "w", encoding="utf-8") as f:
                f.write(content)
            saved_msg = f"Saved to bet_card.txt"
        except Exception as e:
            saved_msg = f"Could not save bet_card.txt: {e}"

        # Show dialog
        dlg = QDialog(self); dlg.setWindowTitle(card_title)
        dlg.setStyleSheet("""
            QDialog { background: #0f0f0f; color: #eaeaea; }
            QTextEdit { background: #101010; color: #eaeaea; font-family: Consolas, 'Courier New', monospace; font-size: 12pt; border: 1px solid #2a2a2a; }
            QPushButton { background: #ff8c2a; color: #111; border-radius: 10px; padding: 6px 12px; font-weight: 700; }
            QPushButton:hover { /* filter removed */ }
            QPushButton:disabled { background: #2a2a2a; color: #777; }
        """)
                # Enforce Bet Card size ~110 x 80 mm (robust + clamped DPI)
        try:
            from PyQt6.QtGui import QGuiApplication
            scr = None
            try:
                h = self.window().windowHandle() if hasattr(self.window(), 'windowHandle') else None
                scr = h.screen() if h is not None else None
            except Exception:
                scr = None
            if scr is None:
                scr = QGuiApplication.primaryScreen()
            ppi = float(scr.logicalDotsPerInch()) if scr is not None else 96.0
            if ppi < 80.0:  ppi = 96.0
            if ppi > 200.0: ppi = 120.0
            w_px = int(round(110.0 * ppi / 25.4))
            h_px = int(round(80.0  * ppi / 25.4))
            w_px = max(w_px, 420)
            h_px = max(h_px, 300)
            dlg.setFixedSize(w_px, h_px)
        except Exception:
            dlg.setFixedSize(420, 300)
        lay = QVBoxLayout(dlg)
        txt = QTextEdit(); txt.setReadOnly(True); txt.setPlainText(content)
        try:
            txt.setStyleSheet("background:#101010; color:#eaeaea; font-family:Consolas, 'Courier New', monospace; font-size:12pt; border:1px solid #2a2a2a;")
        except Exception:
            pass
        lay.addWidget(txt)
        rowBtns = QHBoxLayout()
        bcopy = QPushButton("Copy"); bopen = QPushButton("Open in Notepad"); bclose = QPushButton("Close")
        rowBtns.addWidget(bcopy); rowBtns.addWidget(bopen); rowBtns.addWidget(bclose)
        lay.addLayout(rowBtns)

        def do_copy():
            try:
                QApplication.clipboard().setText(txt.toPlainText())
                QMessageBox.information(self, "Bet Card", "Copied to clipboard. " + saved_msg)
            except Exception:
                QMessageBox.information(self, "Bet Card", "Copied (fallback). " + saved_msg)

        def do_open():
            # try to open bet_card.txt with default editor
            try:
                import subprocess, sys
                root = os.path.dirname(__file__)
                out = os.path.join(root, "bet_card.txt")
                if sys.platform.startswith("win"):
                    os.startfile(out)  # type: ignore[attr-defined]
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", out])
                else:
                    subprocess.Popen(["xdg-open", out])
            except Exception as e:
                QMessageBox.warning(self, "Bet Card", f"Couldn't open file: {e}")

        bcopy.clicked.connect(do_copy)
        bopen.clicked.connect(do_open)
        bclose.clicked.connect(dlg.accept)

        # removed wrong size for Bet Card
        dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
        try: self._bind_settings_fields(dlg)
        except Exception: pass
        dlg.exec()

    def _export_csv(self):
        from pathlib import Path
        import csv, datetime
        out = Path("outputs"); out.mkdir(exist_ok=True, parents=True)
        try:
            for tbl, base in [(self.tblLive,"table1_live_feed"), (self.tblArb,"table2_arbitrage")]:
                if tbl:
                    fp = out / f"{base}_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
                    with fp.open("w", newline="", encoding="utf-8") as f:
                        w = csv.writer(f)
                        headers = [tbl.horizontalHeaderItem(c).text() if tbl.horizontalHeaderItem(c) else f"C{c}" for c in range(tbl.columnCount())]
                        w.writerow(headers)
                        for r in range(tbl.rowCount()):
                            w.writerow([tbl.item(r,c).text() if tbl.item(r,c) else "" for c in range(tbl.columnCount())])
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Export", f"Failed: {e}")

    def _open_settings(self):

        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QCheckBox,

                                     QDialogButtonBox, QPushButton)

        from PyQt6.QtCore import Qt

        dlg = QDialog(self); dlg.setWindowTitle("Settings")

        dlg.setModal(True)
        dlg.setStyleSheet("""
            QDialog { background: #0f0f0f; color: #e5e7eb; border: 1px solid #222; border-radius: 12px; }
            QLabel, QCheckBox { color: #e5e7eb; font-size: 14px; }
            QSlider::groove:horizontal { background: #222; height: 6px; border-radius: 3px; }
            QSlider::handle:horizontal { background: #ff8c2a; width: 14px; margin: -6px 0; border-radius: 7px; }
            QSlider::sub-page:horizontal { background: #ff8c2a; border-radius: 3px; }
            QDialogButtonBox QPushButton, QPushButton {
                background: #ff8c2a; color: #111; border: none; padding: 6px 14px; border-radius: 10px; font-weight: 600;
            }
            QPushButton:hover { /* filter removed */ }
            QPushButton:disabled { background: #2a2a2a; color: #777; }
        """)
        v = QVBoxLayout(dlg)

        try:
            v.setContentsMargins(16,16,16,16)
            v.setSpacing(12)
        except Exception:
            pass
        # (removed) Ding enable + volume block per AA spec

        # Edge threshold (min %)
        rowEdge = QHBoxLayout()
        lblEdge = QLabel("Edge ≥ %", dlg)
        from PyQt6.QtWidgets import QDoubleSpinBox as _QDSB
        spnEdge = _QDSB(dlg); spnEdge.setRange(0.0, 100.0); spnEdge.setSingleStep(0.1)
        try:
            spnEdge.setValue(float(getattr(self, "ding_edge_min", float(self.cfg.get("ding_edge_min", 3.0)))))
        except Exception:
            spnEdge.setValue(3.0)
        rowEdge.addWidget(lblEdge); rowEdge.addWidget(spnEdge, 1)
        spnEdge.setObjectName("Edge")
        v.addLayout(rowEdge)

        # Profit threshold (GBP)
        rowProfit = QHBoxLayout()
        lblProfit = QLabel("Profit ≥ £", dlg)
        spnProfit = _QDSB(dlg); spnProfit.setRange(0.0, 1_000_000.0); spnProfit.setDecimals(2); spnProfit.setSingleStep(1.0)
        try:
            spnProfit.setValue(float(getattr(self, "ding_profit_min", float(self.cfg.get("ding_profit_min", 10.0)))))
        except Exception:
            spnProfit.setValue(10.0)
        rowProfit.addWidget(lblProfit); rowProfit.addWidget(spnProfit, 1)
        spnProfit.setObjectName("Profit")
        v.addLayout(rowProfit)

        # Self-check toggle

        chkSanity = QCheckBox("Show startup self-check", dlg)

        chkSanity.setChecked(bool(getattr(self, "sanity_check_enabled", True)))

        v.addWidget(chkSanity)

        # Test Ding

        # Buttons

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dlg); v.addWidget(btns)

        def accept():
            try:
                # Read values from the spinners
                edge = float(spnEdge.value())
                prof = float(spnProfit.value())
                self.sanity_check_enabled = bool(chkSanity.isChecked())
                # Persist via SettingsBinder if available
                binder = getattr(self, "_settings_binder", None)
                if binder is None:
                    try:
                        binder = _SettingsBinder(self)
                        self._settings_binder = binder
                    except Exception:
                        binder = None
                if binder is not None:
                    self.ding_edge_min = edge; self.ding_profit_min = prof; binder._set_thresholds(edge=edge, profit=prof, persist=True)
                else:
                    # Fallback to config_loader if binder is unavailable
                    try:
                        from config_loader import load_config, save_config
                        cfg = {}
                        try:
                            cfg = load_config()
                        except Exception:
                            cfg = {}
                        cfg["ding_edge_min"] = float(edge)
                        cfg["ding_profit_min"] = float(prof)
                        cfg["sanity_check_enabled"] = bool(self.sanity_check_enabled)
                        save_config(cfg)
                        self.cfg = cfg
                    except Exception:
                        pass
            except Exception:
                pass
            dlg.accept()
# thresholds & persistence
        try:
            pass
        except Exception:
            pass
        try:
            pass
        except Exception:
            pass
        try:
            cfg = load_config()
            cfg["ding_enabled"] = bool(self.ding_enabled)
            cfg["ding_volume"]  = int(self.ding_volume)
            cfg["ding_edge_min"] = float(self.ding_edge_min)
            cfg["ding_profit_min"] = float(self.ding_profit_min)
            cfg["sanity_check_enabled"] = bool(self.sanity_check_enabled)
            save_config(cfg); self.cfg = cfg
        except Exception:
            pass
        dlg.accept()

        btns.accepted.connect(accept); btns.rejected.connect(dlg.reject)

        try: self._bind_settings_fields(dlg)
        except Exception: pass
        dlg.exec()

    def _play_test(self):
        try:
            if hasattr(self.db, "_ding"):
                self.db._ding.play()
        except Exception:
            pass

    def apply_and_close(self):
        try:
            en = self.chk.isChecked()
            vol = self.sld.value()/100.0
            edge = float(self.spnEdge.value())
            prof = float(self.spnProfit.value())
            if self.db is not None:
                self.db.ding_enabled = en
                self.db.ding_volume = vol
                self.db.ding_edge_min = edge
                self.db.ding_profit_min = prof
                if hasattr(self.db, "_ding"):
                    self.db._ding.setVolume(max(0.0, min(1.0, vol)))
            cfg = load_config()
            cfg["ding_enabled"]=en; cfg["ding_volume"]=vol
            cfg["ding_edge_min"]=edge; cfg["ding_profit_min"]=prof
            save_config(cfg)
        except Exception:
            pass
        self.accept()

def _compute_window_title():
    try:
        import os
        from pathlib import Path
        base = "Sports Arbitrage Bot"
        here = Path(__file__).resolve()
        folder = here.parent.name
        return f"{base} — {folder}"
    except Exception:
        return "Sports Arbitrage Bot"

    def _accent_green_hex_from_table(self) -> str:
        """Return Table 1 highlight colour as #RRGGBB, fallback to theme green."""
        try:
            c = getattr(self, 'tblLive').palette().highlight().color()
            return f"#{c.red():02x}{c.green():02x}{c.blue():02x}"
        except Exception:
            return "#1aff97"
    def _open_exit_dialog(self):
        try:
            from exit_dialog_custom import ExitDialog
        except Exception:
            QtWidgets.QMessageBox.warning(self, "Exit", "Exit dialog not available.")
            return
        dlg = ExitDialog(self, accent_color=self._accent_green_hex_from_table(), body_font=self.tblLive.font())
        if dlg.exec():
            QtWidgets.QApplication.instance().quit()
class MainWindow(QMainWindow):

    def _fit_table2_columns(self):
        """Fit Table 2 nicely: Bookmaker stretches; numeric cols compact with min/max clamps."""
        try:
            from PyQt6.QtWidgets import QTableWidget, QTableView, QHeaderView
            from PyQt6.QtCore import Qt
            # Locate Table 2 either on the window or inside the dashboard
            tbl = getattr(self, "table2", None)
            if tbl is None:
                dash = getattr(self, "dashboard", None)
                if dash is not None:
                    tbl = getattr(dash, "table2", None) or getattr(dash, "table", None)
            if tbl is None:
                return
            header = getattr(tbl, "horizontalHeader", lambda: None)()
            if header is None:
                return
            # Reasonable defaults to prevent extremes
            try:
                header.setStretchLastSection(False)
                header.setMinimumSectionSize(60)
                header.setDefaultSectionSize(100)
            except Exception:
                pass
            # Generic helpers
            def clamp_width(set_width, current, lo, hi):
                w = current
                if w < lo: w = lo
                if w > hi: w = hi
                set_width(w)
            def apply_policy(get_label, set_mode, get_width, set_width, colcount):
                labels = { get_label(i): i for i in range(colcount) }
                # Desired sizing
                plan = [
                    ("Bookmaker", ("stretch", 140, 700)),
                    ("Outcome",   ("contents", 80, 140)),
                    ("Back Odds", ("contents", 70, 120)),
                    ("Lay Odds",  ("contents", 70, 120)),
                    ("Edge %",    ("contents", 80, 130)),
                    ("Stake",     ("contents", 90, 150)),
                    ("Profit",    ("contents", 100, 170)),
                ]
                for name, (mode, lo, hi) in plan:
                    c = labels.get(name)
                    if c is None:
                        continue
                    if mode == "stretch":
                        try: set_mode(c, QHeaderView.ResizeMode.Stretch)
                        except Exception: pass
                        try:
                            # allow Qt to compute then clamp
                            tbl.resizeColumnToContents(c)
                            clamp_width(lambda w: tbl.setColumnWidth(c, w), tbl.columnWidth(c), lo, hi)
                        except Exception: pass
                    else:
                        try: set_mode(c, QHeaderView.ResizeMode.ResizeToContents)
                        except Exception: pass
                        try:
                            tbl.resizeColumnToContents(c)
                            clamp_width(lambda w: tbl.setColumnWidth(c, w), tbl.columnWidth(c), lo, hi)
                        except Exception: pass
            # QTableWidget path
            from PyQt6.QtWidgets import QTableWidget
            if isinstance(tbl, QTableWidget):
                def get_label(i):
                    it = tbl.horizontalHeaderItem(i)
                    return "" if it is None else str(it.text())
                def set_mode(i, mode):
                    try: header.setSectionResizeMode(i, mode)
                    except Exception: pass
                def get_width(i):
                    try: return tbl.columnWidth(i)
                    except Exception: return 100
                def set_width(i, w):
                    try: tbl.setColumnWidth(i, w)
                    except Exception: pass
                apply_policy(get_label, set_mode, get_width, set_width, tbl.columnCount())
                try: tbl.resizeRowsToContents()
                except Exception: pass
                return
            # QTableView path
            from PyQt6.QtWidgets import QTableView
            if isinstance(tbl, QTableView):
                mdl = tbl.model()
                if mdl is None:
                    return
                def get_label(i):
                    try: return str(mdl.headerData(i, header.orientation()))
                    except Exception: return ""
                def set_mode(i, mode):
                    try: header.setSectionResizeMode(i, mode)
                    except Exception: pass
                def get_width(i):
                    try: return tbl.columnWidth(i)
                    except Exception: return 100
                def set_width(i, w):
                    try: tbl.setColumnWidth(i, w)
                    except Exception: pass
                apply_policy(get_label, set_mode, get_width, set_width, mdl.columnCount())
                try: tbl.resizeRowsToContents()
                except Exception: pass
        except Exception:
            pass

    def _arm_table2_fit(self):
        """Run the fitter multiple times to catch late population/refreshes."""
        try:
            from PyQt6.QtCore import QTimer
            for d in (0, 150, 400, 900, 1800, 4000, 8000):
                QTimer.singleShot(d, lambda self=self: self._fit_table2_columns())
        except Exception:
            pass
    def _normalize_fetch_spinbox(self):
        """Ensure 'Fetch every' uses whole seconds, 1-click per second."""
        try:
            spn = getattr(self, "spnSecs", None)
            if spn is None:
                return
            # If it's a QDoubleSpinBox, clamp to integer seconds
            try:
                spn.setDecimals(0)
            except Exception:
                pass
            try:
                spn.setSingleStep(1)
            except Exception:
                pass
            try:
                spn.setRange(1, 86400)  # 1s to 24h
            except Exception:
                pass
        except Exception:
            pass

    def _polish_spinboxes(self):
        """Ensure visible +/− on all spin boxes using UpDownArrows and explicit images."""
        try:
            from PyQt6.QtWidgets import QSpinBox, QDoubleSpinBox, QAbstractSpinBox
            import os
            p = os.path.join(os.path.dirname(__file__), "icons").replace("\\", "/")
            css = (
                "QAbstractSpinBox { padding-right: 28px; }\n"
                "QAbstractSpinBox::up-button, QAbstractSpinBox::down-button { subcontrol-origin: border; width: 22px; margin:0; padding:0; border:0; background: transparent; }\n"
                f"QAbstractSpinBox::up-arrow  {{ image: url('{p}/pm_plus_white.png');  width:14px; height:14px; }}\n"
                f"QAbstractSpinBox::down-arrow{{ image: url('{p}/pm_minus_white.png'); width:14px; height:14px; }}\n"
            )
            # Apply at the window level so it wins
            try:
                self.window().setStyleSheet(self.window().styleSheet() + "\n" + css)
            except Exception:
                try:
                    self.setStyleSheet(self.styleSheet() + "\n" + css)
                except Exception:
                    pass
            # Ensure widgets actually show the buttons
            for w in self.findChildren((QSpinBox, QDoubleSpinBox)):
                try:
                    w.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
                except Exception:
                    pass
        except Exception:
            pass
        try:
            pass
        except Exception:
            pass
    def _beautify_spinboxes_ui(self):
        from PyQt6.QtWidgets import QSpinBox, QDoubleSpinBox
        SPIN_CSS = """
        QAbstractSpinBox {
            padding-right: 28px;
            border: 2px solid #24ff6a;
            border-radius: 10px;
            background: #0e0e0e;
            color: #e8e8e8;
            selection-background-color: #24ff6a;
            selection-color: #0e0e0e;
            min-height: 34px;
            font-weight: 600;
        }
        QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {
            subcontrol-origin: padding;
            width: 26px; height: 18px;
            margin: 2px 2px 2px 0;
            border: 2px solid #24ff6a;
            border-radius: 8px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 #ff9a3c, stop:1 #ff7a00);
        }
        QAbstractSpinBox::up-button:hover, QAbstractSpinBox::down-button:hover {
            /* filter removed */
        }
        QAbstractSpinBox::up-button:pressed, QAbstractSpinBox::down-button:pressed {
            background: #ff6a00;
        }
        QAbstractSpinBox::up-button { subcontrol-position: right top; }
        QAbstractSpinBox::down-button { subcontrol-position: right bottom; }
        """
        for w in self.findChildren((QSpinBox, QDoubleSpinBox)):
            w.setStyleSheet(SPIN_CSS)
    def _apply_title(self):
        try:
            folder = _infer_mother_folder()
            self.setWindowTitle(_compute_window_title())
        except Exception:
            pass

    def showEvent(self, event):
        try:
            self._apply_title()
        except Exception:
            pass
        try:
            super().showEvent(event)
        except Exception:
            try:
                super(type(self), self).showEvent(event)
            except Exception:
                pass
    def __init__(self):
        try:
            QTimer.singleShot(0, self._safe_install_settings)
        except Exception:
            pass
        super().__init__()
        self.setWindowTitle(_compute_window_title())
        icon_path = ICON_ICO if os.path.exists(ICON_ICO) else None
        if icon_path: self.setWindowIcon(QtGui.QIcon(icon_path))
        self.statusBar().showMessage("Ready")
        self.dashboard = Dashboard(self, status_cb=self.statusBar().showMessage)
        self.setCentralWidget(self.dashboard)
        self._beautify_spinboxes_ui()
        self._polish_spinboxes()
        self._normalize_fetch_spinbox()

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

    def _wire_bet_button_exact(self):
        """
        Force-wire the Bet Card button that lives under self.calcBox (calculator panel).
        Prefers an existing self.btnBetCard; otherwise finds a QPushButton in calcBox
        whose text contains 'bet' and 'card'. Connect both clicked & pressed.
        Adds a thin green outline and '(wired)' tooltip so we can confirm it.
        """
        try:
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

    def _wire_calcbox_bet_button(self):
        """
        Find the Bet Card button under self.calcBox and wire it (clicked & pressed) to _open_bet_card.
        Add a green outline and '(wired)' tooltip as confirmation.
        Returns True if wired, else False.
        """
        try:
            btn = getattr(self, "btnBetCard", None)
            if btn is None and hasattr(self, "calcBox"):
                for w in self.calcBox.findChildren(QtWidgets.QPushButton):
                    t = (w.text() or "").lower()
                    n = (w.objectName() or "").lower()
                    if ("bet" in t and "card" in t) or ("bet" in n and "card" in n):
                        btn = w
                        break
            if btn is None:
                return False
            self.btnBetCard = btn
            try:
                try: btn.clicked.disconnect()
                except Exception: pass
                try: btn.pressed.disconnect()
                except Exception: pass
            except Exception:
                pass
            try:
                if callable(getattr(self, "status_cb", None)):
                    btn.clicked.connect(lambda: self.status_cb("Bet Card (button)"))
            except Exception:
                pass
            try: btn.clicked.connect(self._open_bet_card)
            except Exception: pass
            try: btn.pressed.connect(self._open_bet_card)
            except Exception: pass
            try: btn.setEnabled(True); btn.setVisible(True)
            except Exception: pass
            try:
                ss = btn.styleSheet() or ""
                if "outline: 2px solid #3c3" not in ss:
                    btn.setStyleSheet(ss + " ; outline: 2px solid #3c3;")
                tip = (btn.toolTip() or "")
                if "(wired)" not in tip:
                    btn.setToolTip((tip + "  (wired)").strip())
            except Exception:
                pass
            return True
        except Exception as e:
            print("wire_calcbox_bet_button error", e)
            return False

    def _wire_calcbox_bet_button_with_retries(self):
        """Retry at 0ms, 500ms, 1000ms to catch late UI replacements."""
        from PyQt6.QtCore import QTimer
        delays = [0, 500, 1000]
        def attempt(i=0):
            ok = self._wire_calcbox_bet_button()
            try:
                if callable(getattr(self, "status_cb", None)):
                    self.status_cb(f"Bet Card wiring (calcBox) try {i+1}/{len(delays)} -> {'OK' if ok else 'no button yet'}")
            except Exception:
                pass
            if not ok and i+1 < len(delays):
                QTimer.singleShot(delays[i+1], lambda: attempt(i+1))
        attempt(0)

    def _scan_and_wire_bet_buttons(self):
        """Scan all QPushButtons; wire anything that looks like Bet Card. Idempotent."""
        try:
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

# --- Startup sanity check (removable) ---
def run_ui_sanity_check(window, allow_disable=True):
    """Validate invariants; disable via Settings or ARB_SANITY_CHECK=0."""
    try:
        from PyQt6.QtWidgets import QMessageBox, QTabWidget, QTableWidget, QTableView
        from PyQt6.QtCore import Qt
        import os as _os
        issues=[]
        try:
            if isinstance(window.centralWidget(), QTabWidget):
                issues.append("Central widget is a TabWidget (tabs should be removed).")
        except Exception: pass
        try:
            dash = getattr(window, "dashboard", None) or window
            tbl = getattr(dash, "tblArb", None) or getattr(dash, "table2", None) or getattr(dash, "table", None)
            if tbl is None:
                issues.append("Table 2 not found.")
            else:
                if isinstance(tbl, QTableWidget):
                    headers=[(tbl.horizontalHeaderItem(i).text() if tbl.horizontalHeaderItem(i) else "") for i in range(tbl.columnCount())]
                else:
                    mdl=tbl.model()
                    headers=[str(mdl.headerData(i, Qt.Orientation.Horizontal)) for i in range(mdl.columnCount())] if mdl else []
                if "Profit" not in headers: issues.append('Missing "Profit" column/header on Table 2.')
                if len(headers) < 7: issues.append("Table 2 has fewer than 7 columns (should be 7).")
        except Exception as e:
            issues.append(f"Header check error: {e}")
        dash = getattr(window, "dashboard", None) or window
        wav_path=None
        if hasattr(dash, "_ensure_ding_asset"):
            wav_path = dash._ensure_ding_asset()
        if not wav_path or not _os.path.exists(wav_path):
            issues.append("assets/ding.wav not found/created.")
        if issues:
            QMessageBox.warning(window, "UI Self-Check", "Startup self-check found issues:\n\n" + "\n".join("• "+i for i in issues))
        else:
            if allow_disable:
                QMessageBox.information(window, "UI Self-Check", "All core checks passed. Disable in Settings or set ARB_SANITY_CHECK=0.")
    except Exception:
        pass

def _reinstate_spin_arrows(self):
    """
    Ensure all spin boxes (QSpinBox/QDoubleSpinBox) show +/− arrows.
    - Forces ButtonSymbols.UpDownArrows (in case they were set to NoButtons).
    - Applies padding and arrow images.
    """
    try:
        from PyQt6.QtWidgets import QAbstractSpinBox
        import os
        p = os.path.join(os.path.dirname(__file__), "icons").replace("\\", "/")
        css = f"""
QAbstractSpinBox {{
    padding-right: 26px;
}}
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{
    subcontrol-origin: border;
    width: 22px; border: 0; background: transparent;
}}
QAbstractSpinBox::up-button   {{ subcontrol-position: top right;    }}
QAbstractSpinBox::down-button {{ subcontrol-position: bottom right; }}
QDoubleSpinBox::up-arrow  {{ image: url("{p}/pm_plus.png");  }}
QDoubleSpinBox::down-arrow{{ image: url("{p}/pm_minus.png"); }}
QSpinBox::up-arrow        {{ image: url("{p}/pm_plus.png");  }}
QSpinBox::down-arrow      {{ image: url("{p}/pm_minus.png"); }}
"""
        # Apply to window (highest priority) and re-enable built-in buttons
        try:
            self.window().setStyleSheet(self.window().styleSheet() + "\\n" + css)
        except Exception:
            try:
                self.setStyleSheet(self.styleSheet() + "\\n" + css)
            except Exception:
                pass

        for sp in self.findChildren(QAbstractSpinBox):
            try:
                sp.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
            except Exception:
                pass
    except Exception:
        pass
def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(); w.resize(1366, 820); w.showMaximized()
    try:
        import os as _os
        dash = getattr(w, "dashboard", None) or w
        enabled = bool(getattr(dash, "sanity_check_enabled", True))
        if _os.environ.get("ARB_SANITY_CHECK","1") == "1" and enabled:
            run_ui_sanity_check(w, allow_disable=True)
    except Exception:
        pass
    try:
        w._arm_table2_fit()
    except Exception:
        pass

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

# __wire_logout helper appended (v2)
def _wire_logout_v2(dash):
    '''
    Connect anything that looks like "Logout" to dash._logout() if present,
    otherwise to the styled dialog fallback.
    '''
    try:
        from PyQt6.QtWidgets import QPushButton, QToolButton
        from PyQt6.QtGui import QAction
    except Exception:
        QPushButton = QToolButton = QAction = None

    def norm(t):
        if not t: return ''
        import re
        return re.sub(r'\s+', ' ', str(t).strip().lower()).replace('&','')

    # choose target
    fn = getattr(dash, '_logout', None)
    if not callable(fn):
        fn = lambda: _styled_logout_dialog_v2(dash)

    # by attribute
    for name in ('btnLogout', 'logoutButton', 'buttonLogout'):
        try:
            w = getattr(dash, name, None)
            if w is not None and hasattr(w, 'clicked'):
                try: w.clicked.disconnect()
                except Exception: pass
                w.clicked.connect(fn)
                return True
        except Exception:
            pass

    # by visible text/name
    try:
        btns = []
        if QPushButton: btns += dash.findChildren(QPushButton)
        if QToolButton: btns += dash.findChildren(QToolButton)
    except Exception:
        btns = []
    for b in btns:
        label = norm(getattr(b, 'text', lambda: '')())
        name  = norm(getattr(b, 'objectName', lambda: '')())
        if label in ('logout','log out') or name in ('logout','log out'):
            try:
                try: b.clicked.disconnect()
                except Exception: pass
                b.clicked.connect(fn)
                return True
            except Exception:
                pass

    # actions
    try:
        acts = dash.findChildren(QAction)
    except Exception:
        acts = []
    for a in acts:
        txt = norm(getattr(a, 'text', lambda:'')())
        tip = norm(getattr(a, 'toolTip', lambda:'')())
        nm  = norm(getattr(a, 'objectName', lambda:'')())
        if txt in ('logout','log out') or tip in ('logout','log out') or nm in ('logout','log out'):
            try:
                try: a.triggered.disconnect()
                except Exception: pass
                a.triggered.connect(fn)
                return True
            except Exception:
                pass
    return False

    def _compute_profit_from_row(self, row_dict):
        try: stake = float(row_dict.get("Stake", "") or 0)
        except Exception: stake = 0.0
        try:
            edge_raw = str(row_dict.get("Edge %", "")).replace("%","").strip()
            edge = float(edge_raw) if edge_raw else 0.0
        except Exception: edge = 0.0
        return round(stake * edge / 100.0, 2)

    def _safe_install_settings(self):
        """Robustly populate the Settings tab with Ding controls; never leave a white screen."""
        try:
            # Locate a QTabWidget (prefer self.tabs)
            tabw = getattr(self, "tabs", None)
            if tabw is None:
                tabs = self.findChildren(QTabWidget)
                if tabs: tabw = tabs[0]
            if tabw is None:
                return

            # Locate "Settings" tab by title
            idx = None
            for i in range(tabw.count()):
                try:
                    if tabw.tabText(i).strip().lower() == "settings":
                        idx = i; break
                except Exception:
                    pass
            if idx is None:
                return
            sw = tabw.widget(idx)

            # If already installed, skip
            if getattr(sw, "_ding_installed", False):
                return

            # Ensure layout
            if sw.layout() is None:
                root = QVBoxLayout(sw)
                root.setContentsMargins(16,16,16,16)
                root.setSpacing(12)
            else:
                root = sw.layout()

            # Build group
            grp = QGroupBox("Ding Alerts", sw)
            form = QFormLayout(grp)
            form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

            # Enabled
            try:
                en = bool(self.dashboard.ding_enabled)
            except Exception:
                en = True
            self.chkDing.setChecked(en)
            # Volume
            try:
                vol = int(max(0.0, min(1.0, float(getattr(self.dashboard, "ding_volume", 0.5))))*100)
            except Exception:
                vol = 50
            # Edge threshold
            self.spnEdge = QDoubleSpinBox(grp); self.spnEdge.setDecimals(1); self.spnEdge.setRange(0.0, 100.0); self.spnEdge.setSingleStep(0.1)
            try:
                self.spnEdge.setValue(float(getattr(self.dashboard, "ding_edge_min", 3.0)))
            except Exception:
                self.spnEdge.setValue(3.0)
            form.addRow("Edge ≥ %", self.spnEdge)

            # Profit threshold
            self.spnProfit = QDoubleSpinBox(grp); self.spnProfit.setDecimals(2); self.spnProfit.setRange(0.0, 1_000_000.0); self.spnProfit.setSingleStep(1.0)
            try:
                self.spnProfit.setValue(float(getattr(self.dashboard, "ding_profit_min", 10.0)))
            except Exception:
                self.spnProfit.setValue(10.0)
            form.addRow("Profit ≥", self.spnProfit)

            # Test button
            row = QHBoxLayout()
            row.addStretch(1); row.addWidget(btnTest)
            form.addRow("", row)

            root.addWidget(grp)
            root.addStretch(1)

            def _apply():
                try:
                    en = self.chkDing.isChecked()
                    vol = float(getattr(self.dashboard, "ding_volume", 0.7))
                    edge = float(self.spnEdge.value())
                    prof = float(self.spnProfit.value())
                    # live apply
                    if hasattr(self, "dashboard"):
                        self.dashboard.ding_enabled = en
                        self.dashboard.ding_volume  = vol
                        self.dashboard.ding_edge_min = edge
                        self.dashboard.ding_profit_min = prof
                        if hasattr(self.dashboard, "_ding"):
                            self.dashboard._ding.setVolume(max(0.0, min(1.0, vol)))
                    # persist
                    cfg = load_config()
                    cfg["ding_enabled"] = en
                    cfg["ding_volume"] = vol
                    cfg["ding_edge_min"] = edge
                    cfg["ding_profit_min"] = prof
                    save_config(cfg)
                    try:
                        self.statusBar().showMessage(f"Ding: {'On' if en else 'Off'} @ {int(vol*100)}% | Edge≥{edge} Profit≥{prof}")
                    except Exception:
                        pass
                except Exception:
                    pass

            self.chkDing.stateChanged.connect(lambda *_: _apply())
            self.spnEdge.valueChanged.connect(lambda *_: _apply())
            self.spnProfit.valueChanged.connect(lambda *_: _apply())
            sw._ding_installed = True
        except Exception as e:
            # Fail-safe: display an error label instead of a blank tab
            try:
                holder = sw if 'sw' in locals() and sw else self
                if hasattr(holder, 'layout') and callable(holder.layout) and holder.layout() is None:
                    QVBoxLayout(holder)
                if hasattr(holder, 'layout') and holder.layout():
                    holder.layout().addWidget(QLabel(f"Settings failed to load: {e}"))
            except Exception:
                pass

def _remove_settings_tabs_here(widget):
    try:
        tabs = widget.findChildren(QTabWidget)
        for tw in tabs:
            i = 0
            while i < tw.count():
                try:
                    if tw.tabText(i).strip().lower() == 'settings':
                        tw.removeTab(i); continue
                except Exception:
                    pass
                i += 1
    except Exception:
        pass

def _ensure_profit_column(tbl):
    """Ensure 'Profit' exists as last column and is £ formatted; derive if needed from Stake & Edge %."""
    from PyQt6.QtWidgets import QTableWidgetItem
    import re as _re
    # find header index for Profit
    cols = tbl.columnCount()
    labels = [tbl.horizontalHeaderItem(i).text() if tbl.horizontalHeaderItem(i) else "" for i in range(cols)]
    if "Profit" not in labels:
        tbl.insertColumn(cols); tbl.setHorizontalHeaderItem(cols, QTableWidgetItem("Profit"))
    # refresh cols info
    cols = tbl.columnCount(); labels = [tbl.horizontalHeaderItem(i).text() if tbl.horizontalHeaderItem(i) else "" for i in range(cols)]
    try:
        stake_idx = labels.index("Stake")
    except ValueError:
        stake_idx = -1
    try:
        edge_idx = labels.index("Edge %")
    except ValueError:
        edge_idx = -1
    prof_idx = labels.index("Profit")
    rows = tbl.rowCount()
    for r in range(rows):
        # get stake number
        def _num(s):
            try:
                return float(str(s).replace('£','').replace(',','').strip())
            except Exception:
                return 0.0
        stake_val = 0.0
        edge_val = 0.0
        if stake_idx >= 0:
            it = tbl.item(r, stake_idx)
            stake_val = _num(it.text() if it else 0)
        if edge_idx >= 0:
            it = tbl.item(r, edge_idx)
            if it:
                txt = it.text().replace('%','').strip()
                try: edge_val = float(txt)
                except Exception: edge_val = 0.0
        profit = round(stake_val * edge_val / 100.0, 2)
        item = QTableWidgetItem(f"£ {profit:,.2f}")
        tbl.setItem(r, prof_idx, item)
    try:
        tbl.resizeColumnsToContents()
    except Exception:
        pass


# === Runtime patches (Y) ===
try:
    import settings_patch as _sp; _sp.apply(Dashboard)
except Exception: pass
try:
    import audio_patch as _ap; _ap.apply(Dashboard)
except Exception: pass
try:
    import ui_patch as _up; _up.apply(Dashboard)
except Exception: pass