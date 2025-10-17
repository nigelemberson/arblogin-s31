import os as _os
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
    def _wire_toggle_styles(self):
        """Minimal & theme-safe: independent wiring, no font/size changes, no colored borders."""
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

        spn = getattr(self, "spnSecs", None)
        if spn is None:
            for c in self.findChildren((QSpinBox, QDoubleSpinBox)):
                name = (c.objectName() or "").lower()
                if "sec" in name or "fetch" in name:
                    spn = c
                    break

        def style_btn(b, bg, fg):
            try:
                b.setStyleSheet(f"background:{bg}; color:{fg}; border:none;")
            except Exception:
                pass

        # Button 4: Auto Refresh (update its text On/Off)
        if auto_refresh_btn:
            try: auto_refresh_btn.setCheckable(True)
            except Exception: pass
            def _style_auto(on, b=auto_refresh_btn):
                try:
                    b.setText("Auto Refresh: On" if on else "Auto Refresh: Off")
                    if on: style_btn(b, "#20d070", "#111")
                    else:  style_btn(b, "#ff7a1a", "#111")
                except Exception:
                    pass
            _style_auto(auto_refresh_btn.isChecked())
            try: auto_refresh_btn.toggled.disconnect()
            except Exception: pass
            auto_refresh_btn.toggled.connect(lambda on, b=auto_refresh_btn: _style_auto(on, b))

        # Button 3: Fetch Auto API (no label change; disable spnSecs while ON)
        if auto_fetch_btn:
            try: auto_fetch_btn.setCheckable(True)
            except Exception: pass
            def _style_fetch(on, b=auto_fetch_btn):
                try:
                    if on: style_btn(b, "#20d070", "#111")
                    else:  style_btn(b, "#ff7a1a", "#111")
                    if spn: spn.setEnabled(not on)
                except Exception:
                    pass
            _style_fetch(auto_fetch_btn.isChecked())
            try: auto_fetch_btn.toggled.disconnect()
            except Exception: pass
            auto_fetch_btn.toggled.connect(lambda on, b=auto_fetch_btn: _style_fetch(on, b))

    # No-op styling hook to avoid QObject init errors if called before super().__init__()
    def _beautify_spinboxes(self):
        return
    def __init__(self, parent=None, status_cb=None):
        super().__init__(parent)
        self.status_cb = status_cb or (lambda s: None)
        self.cfg = load_config()
        self._api_key = self.cfg.get("odds_api_key","")
        self._auto_copy = bool(self.cfg.get("auto_copy", False))
        self.feed = OddsFeed(lambda: self._api_key)
        self.auto_timer = QTimer(self); self.auto_timer.timeout.connect(self._fetch_now)
        self.setStyleSheet(APP_QSS)
        self._build_ui()
        try:
            self._wire_toggle_styles()
        except Exception:
            pass

        # ensure Logout is wired (v2)
        try:
            _wire_logout_v2(self)
        except Exception:
            pass
        # schedule once after show
        try:
            import PyQt6.QtCore as _QtCore
            _QtCore.QTimer.singleShot(0, lambda: _wire_logout_v2(self))
        except Exception:
            pass

        self._fill_demo_data()

    def _build_ui(self):
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(12,8,12,10)
        self.grid.setHorizontalSpacing(12); self.grid.setVerticalSpacing(10)

        self.titleBox = QFrame(objectName="titleBox"); self.titleBox.setStyleSheet(PANEL_BORDER)
        layT = QHBoxLayout(self.titleBox); layT.setContentsMargins(16,8,16,8); layT.setSpacing(12)
        self.logo = QLabel()
        icon_path = ICON_PNG if os.path.exists(ICON_PNG) else (ICON_ICO if os.path.exists(ICON_ICO) else None)
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
        self._apply_plus_minus_icons()
        self.controlsBox = QFrame(objectName="controlsBox"); self.controlsBox.setStyleSheet(PANEL_BORDER)
        v = QVBoxLayout(self.controlsBox); v.setContentsMargins(16,12,16,12); v.setSpacing(10)
        cap = QLabel("Controls"); cap.setStyleSheet("font-weight:800; font-size:18px;"); v.addWidget(cap)
        def add_btn(text):
            b = QPushButton(text); b.setStyleSheet(BTN_ORANGE); b.setMinimumHeight(46); b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed); v.addWidget(b); return b
        self.btnRefresh   = add_btn("Refresh Odds / Arbs")
        self.btnFetchNow  = add_btn("Fetch One API")
        self.btnAutoFetch = add_btn("Fetch Auto API")
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
        self.btnLogout = add_btn("Logout"); self.btnKey = add_btn("Key...")
        v.addStretch(1)

        # wire control buttons
        self.btnKey.clicked.connect(self._open_key_dialog)
        # Safe dynamic wiring (skips missing/late-created widgets)
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

        self.btnFetchNow.clicked.connect(self._fetch_now)
        self.btnAutoFetch.clicked.connect(self._toggle_auto_fetch)

        self.centerBox = QFrame(objectName="centerBox"); self.centerBox.setStyleSheet(PANEL_BORDER)
        vc = QVBoxLayout(self.centerBox); vc.setContentsMargins(14,10,14,10); vc.setSpacing(8)

        headerRow = QHBoxLayout(); headerRow.setContentsMargins(0,0,0,0)
        cap1 = QLabel("Table 1: Live Feed"); cap1.setStyleSheet("font-weight:800; font-size:18px;")
        headerRow.addWidget(cap1, 0, Qt.AlignmentFlag.AlignLeft)
        headerRow.addStretch(1)
        self.btnQuota = QPushButton("Quota: demo"); self.btnQuota.setStyleSheet("QPushButton{background:#0f0f0f;color:#cfead9;padding:6px 10px;border-radius:14px;border:2px solid %s;font-weight:800;font-size:13px;}" % CLR_GREEN); self.btnQuota.setFixedHeight(28)
        try:
            self.btnQuota.clicked.disconnect()
        except Exception:
            pass
        self.btnQuota.clicked.connect(self._show_quota_details)
        headerRow.addWidget(self.btnQuota, 0, Qt.AlignmentFlag.AlignRight)
        vc.addLayout(headerRow)

        self.tblLive = QTableWidget(0,6); self.tblLive.setHorizontalHeaderLabels(["Sport","League","Match","Book","Price","Time"]); vc.addWidget(self.tblLive)
        self.tblLive.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tblLive.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tblLive.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.lblReload1 = QLabel("Last reload: demo"); self.lblReload1.setStyleSheet("color:#9fd; font-size:16px;"); vc.addWidget(self.lblReload1)

        cap2 = QLabel("Table 2: Arbitrage Opportunities"); cap2.setStyleSheet("font-weight:800; font-size:18px;"); vc.addWidget(cap2)
        self.tblArb = QTableWidget(0,6); self.tblArb.setHorizontalHeaderLabels(["Bookmaker","Outcome","Back Odds","Lay Odds","Edge %","Stake"]); vc.addWidget(self.tblArb)
        self.tblArb.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tblArb.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tblArb.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.lblReload2 = QLabel("Last reload: demo"); self.lblReload2.setStyleSheet("color:#9fd; font-size:16px;"); vc.addWidget(self.lblReload2)

        self.calcBox = QFrame(objectName="calcBox"); self.calcBox.setStyleSheet(PANEL_BORDER)
        vx = QVBoxLayout(self.calcBox); vx.setContentsMargins(16,12,16,12); vx.setSpacing(10)
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

        r1 = QHBoxLayout(); r2 = QHBoxLayout()
        def add_btn_calc(text):
            b = QPushButton(text); b.setStyleSheet(BTN_ORANGE); b.setMinimumHeight(46); b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed); return b
        self.btnCalc = add_btn_calc("Calculate"); self.btnClear = add_btn_calc("Clear")
        r1.addWidget(self.btnCalc); r1.addWidget(self.btnClear); vx.addLayout(r1)
        self.btnUseSel = add_btn_calc("Use Selection"); r2.addWidget(self.btnUseSel)
        self.btnAutoCopy = add_btn_calc("Auto Copy"); self.btnAutoCopy.setCheckable(True); self.btnAutoCopy.setChecked(self._auto_copy)
        self.btnAutoCopy.setStyleSheet(BTN_ORANGE + "\nQPushButton:checked { background:#cc6a1a; border-color:#ff9a3a; }\nQPushButton:checked:hover { background:#d87422; }")
        r2.addWidget(self.btnAutoCopy); vx.addLayout(r2)
        self.btnBetCard = add_btn_calc("Bet Card"); vx.addWidget(self.btnBetCard)

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

        # polish tables
        for tbl in (self.tblLive, self.tblArb):
            tbl.setStyleSheet(TABLE_STYLE + HEADER_STYLE)
            tbl.verticalHeader().setVisible(False)
            tbl.verticalHeader().setDefaultSectionSize(32)
            hh: QHeaderView = tbl.horizontalHeader()
            hh.setStretchLastSection(True)
            hh.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            hh.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            tbl.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
            tbl.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
            tbl.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        # Layout grid
        self.grid.addWidget(self.titleBox,0,0,1,2)
        self.grid.addWidget(self.calcBox,0,2,2,1)
        self.grid.addWidget(self.controlsBox,1,0,1,1)
        self.grid.addWidget(self.centerBox,1,1,1,1)
        self.grid.setColumnStretch(0,1); self.grid.setColumnStretch(1,3); self.grid.setColumnStretch(2,1)
        self.grid.setRowStretch(1,1)

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
                self.auto_timer = QTimer(self); self.auto_timer.timeout.connect(self._fetch_now)
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
        if self.tblArb.selectedItems():
            r = self.tblArb.currentRow()
            try:
                back_odds = float(self.tblArb.item(r,2).text())
                lay_odds  = float(self.tblArb.item(r,3).text())
                self.inA.setValue(back_odds);
                if lay_odds>0: self.inB.setValue(lay_odds)
            except Exception: pass
        elif self.tblLive.selectedItems():
            r = self.tblLive.currentRow()
            try:
                price = float(self.tblLive.item(r,4).text())
                self.inA.setValue(price)
            except Exception: pass
        self._calculate()

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

    def _open_bet_card(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton, QMessageBox, QApplication
        dlg = QDialog(self); dlg.setWindowTitle(f"SPORTS ARBITRAGE BOT — Dashboard ({_infer_mother_folder()})")
        lay = QVBoxLayout(dlg)
        txt = QTextEdit()
        txt.setPlainText("Select a row first, then reopen Bet Card.")
        lay.addWidget(txt)
        row = QHBoxLayout(); bcopy = QPushButton("Copy"); bclose = QPushButton("Close")
        row.addWidget(bcopy); row.addWidget(bclose); lay.addLayout(row)
        def do_copy():
            QApplication.clipboard().setText(txt.toPlainText())
            QMessageBox.information(self, "Bet Card", "Copied to clipboard.")
        bcopy.clicked.connect(do_copy); bclose.clicked.connect(dlg.accept)
        dlg.resize(640,420); dlg.exec()

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
        from PyQt6.QtWidgets import QMessageBox, QMainWindow
        parent = self.parent()
        while parent and not isinstance(parent, QMainWindow):
            parent = parent.parent()
        if parent and hasattr(parent, "tabs"):
            try:
                parent.tabs.setCurrentIndex(1)
                if callable(self.status_cb): self.status_cb("Opened Settings")
            except Exception:
                pass
        else:
            QMessageBox.information(self, "Settings", "Settings panel not available.")

    def _open_audit_log(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Audit Log", "No audit entries yet.")
# ---- Dark, readable Yes/No dialog ----
def _ask_yes_no(self, title: str, text: str) -> bool:
    from PyQt6.QtWidgets import QMessageBox, QPushButton
    box = QMessageBox(self)
    box.setWindowTitle(title)
    box.setText(text)
    box.setIcon(QMessageBox.Icon.Question)
    yes = QPushButton("Yes")
    no  = QPushButton("No")
    box.addButton(yes, QMessageBox.ButtonRole.YesRole)
    box.addButton(no,  QMessageBox.ButtonRole.NoRole)
    box.setStyleSheet("""\n""            QMessageBox { background:#0f1115; }
        QLabel { color:#e5e7eb; font-size:14px; }
        QPushButton {
          background:#ff8c2a; color:#111; border:none; padding:6px 12px;
          border-radius:8px; font-weight:600;
        }
        QPushButton:hover { /* filter removed */ }
    ""\n""")
    box.exec()
    return box.clickedButton() is yes

def _logout(self):
        # Compact black/orange dialog identical to your API Key window (self-contained).
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QApplication
        from PyQt6.QtCore import Qt

        dlg = QDialog(self)
        dlg.setWindowTitle("Logout")
        dlg.setModal(True)
        dlg.setStyleSheet("""
            QDialog { background: #0f0f0f; color: #e5e7eb; border: 1px solid #222; border-radius: 12px; }
            QLabel { color: #e5e7eb; font-size: 14px; }
            QPushButton { background: #ff8c2a; color: #111; border: none; padding: 6px 14px; border-radius: 10px; font-weight: 600; }
            QPushButton:hover { /* filter removed */ }
            QPushButton:disabled { background: #2a2a2a; color: #777; }
        """)

        layout = QVBoxLayout(dlg); layout.setContentsMargins(16,16,16,16); layout.setSpacing(14)
        layout.addWidget(QLabel("Exit the application?"), alignment=Qt.AlignmentFlag.AlignLeft)

        row = QHBoxLayout(); row.addStretch(1)
        btn_yes = QPushButton("Yes", dlg); btn_no = QPushButton("No", dlg)
        row.addWidget(btn_yes); row.addWidget(btn_no)
        layout.addLayout(row)

        decided_yes = {"v": False}
        btn_yes.clicked.connect(lambda: (decided_yes.update(v=True), dlg.accept()))
        btn_no.clicked.connect(dlg.reject)
        btn_no.setAutoDefault(True); btn_no.setDefault(True)

        dlg.resize(360, 160)
        dlg.exec()
        if decided_yes["v"]:
            QApplication.quit()

class MainWindow(QMainWindow):

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
        """
        Make spinbox buttons compact and show + / - symbols (not OS arrows).
        This touches both QSpinBox and QDoubleSpinBox found in the window.
        """
        from PyQt6.QtWidgets import QSpinBox, QDoubleSpinBox, QAbstractSpinBox
        try:
            for w in self.findChildren((QSpinBox, QDoubleSpinBox)):
                try:
                    w.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
                except Exception:
                    pass
                w.setStyleSheet("""
                    QAbstractSpinBox {
                        padding-right: 22px;
                        border: 2px solid #24ff6a;
                        border-radius: 10px;
                        background: #0e0e0e;
                        color: #e8e8e8;
                        min-height: 28px;
                        font-weight: 600;
                    }
                    QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {
                        subcontrol-origin: padding;
                        width: 20px; height: 14px;
                        margin: 2px 2px 2px 0;
                        border: 2px solid #24ff6a;
                        border-radius: 8px;
                        background: #ff7a00;
                    }
                    QAbstractSpinBox::up-button:hover, QAbstractSpinBox::down-button:hover {
                        background: #ff9a3c;
                    }
                    QAbstractSpinBox::up-button:pressed, QAbstractSpinBox::down-button:pressed {
                        background: #ff6a00;
                    }
                    QAbstractSpinBox::up-button   { subcontrol-position: right top; }
                    QAbstractSpinBox::down-button { subcontrol-position: right bottom; }
                """)
        except Exception:
            pass
    def _clear(self):
        """Safe placeholder for Clear to avoid crashes."""
        try:
            # Try to clear common output fields if they exist.
            for name in ["txtBackStake", "txtLayStake", "txtProfit", "txtLiability", "txtNotes"]:
                w = getattr(self, name, None)
                if w is not None:
                    try:
                        w.setText("")
                    except Exception:
                        try:
                            w.clear()
                        except Exception:
                            pass
        except Exception:
            pass

    def _toggle_auto_copy(self, checked=False):
        """Safe placeholder toggle; no-op until wired."""
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
            self.setWindowTitle(f"SPORTS ARBITRAGE BOT — Dashboard ({folder})")
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
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        icon_path = ICON_PNG if os.path.exists(ICON_PNG) else (ICON_ICO if os.path.exists(ICON_ICO) else None)
        if icon_path: self.setWindowIcon(QtGui.QIcon(icon_path))
        self.statusBar().showMessage("Ready")
        self.tabs = QTabWidget()
        self.dashboard = Dashboard(self, status_cb=self.statusBar().showMessage)
        self.tabs.addTab(self.dashboard, "Dashboard")
        self.tabs.addTab(QWidget(), "Settings")
        self.setCentralWidget(self.tabs)
        self._beautify_spinboxes_ui()
        self._polish_spinboxes()
        self._normalize_fetch_spinbox()

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(); w.resize(1366, 820); w.showMaximized()
    sys.exit(app.exec())

    def _apply_plus_minus_icons(self):
        """Create simple + / − PNGs and point all QDoubleSpinBox arrows to them."""
        try:
            import os
            from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
            from PyQt6.QtCore import Qt
            icon_dir = os.path.join(os.path.dirname(__file__), "icons")
            os.makedirs(icon_dir, exist_ok=True)
            plus_path  = os.path.join(icon_dir, "pm_plus.png")
            minus_path = os.path.join(icon_dir, "pm_minus.png")

            def make(text, path):
                if not os.path.exists(path):
                    pm = QPixmap(24, 24)
                    pm.fill(Qt.GlobalColor.transparent)
                    p = QPainter(pm)
                    f = QFont()
                    f.setBold(True)
                    f.setPointSize(16)
                    p.setFont(f)
                    p.setPen(QColor("#000000"))
                    p.drawText(pm.rect(), int(Qt.AlignmentFlag.AlignCenter), text)
                    p.end()
                    pm.save(path)

            make("+", plus_path)
            make("−", minus_path)

            p_plus  = plus_path.replace("\\", "/")
            p_minus = minus_path.replace("\\", "/")

            spin_qss = f"""QDoubleSpinBox::up-arrow   {{ image: url("{p_plus}");  width: 12px; height: 12px; }}
QDoubleSpinBox::down-arrow {{ image: url("{p_minus}"); width: 12px; height: 12px; }}
"""
            # Append to existing stylesheet so we don't clobber other styles
            self.setStyleSheet(self.styleSheet() + "\n" + spin_qss)
        except Exception as e:
            # Non-fatal if drawing fails
            pass

if __name__ == "__main__":
    main()

# __wire_logout helper appended (v2)
def _styled_logout_dialog_v2(dash):
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        box = QMessageBox(dash)
        box.setWindowTitle('Logout')
        box.setText('Exit the application?')
        box.setIcon(QMessageBox.Icon.Question)
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        box.setDefaultButton(QMessageBox.StandardButton.No)
        box.setStyleSheet("""\nQMessageBox { background-color:#0e1116; }
'
                          'QLabel { color:#e5e7eb; font-size:14px; }
'
                          'QPushButton { background:#ff8c2a; color:#111; border:none; padding:6px 12px; border-radius:8px; font-weight:600; }
'
                          'QPushButton:hover { /* filter removed */ }\n""")
        if box.exec() == QMessageBox.StandardButton.Yes:
            QApplication.quit()
    except Exception:
        try:
            from PyQt6.QtWidgets import QApplication
            QApplication.quit()
        except Exception:
            pass

def _wire_logout_v2(dash):
    '''
    Connect anything that looks like "Logout" to dash._logout() if present,
    otherwise to the styled dialog fallback.
    '''
    try:
        from PyQt6.QtWidgets import QPushButton, QToolButton, QAction
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
