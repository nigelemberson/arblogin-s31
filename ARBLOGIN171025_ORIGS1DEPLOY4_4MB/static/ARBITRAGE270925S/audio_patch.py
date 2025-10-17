
from PyQt6.QtWidgets import QDialog, QComboBox, QCheckBox, QGridLayout, QPushButton, QLabel, QSlider, QSizePolicy
from PyQt6.QtCore import Qt
from audio_engine import AudioEngine
from config_loader import load_config, save_config

def apply(DashboardClass):
    def _audio_init(self):
        self._audio = AudioEngine()

    def _audio_show_dialog(self):
        try:
            dlg = QDialog(self); dlg.setWindowTitle('Audio Alerts'); g = QGridLayout(dlg)
            dlg.setStyleSheet('QDialog{background:#0b0b0b;} QLabel{color:#e5e7eb;} QComboBox{color:#e5e7eb;} QPushButton{background:#ff7a1a;color:black;border:1px solid #28e37b;border-radius:8px;padding:6px 8px;font-weight:700;}')
            cbE = QCheckBox('Enable audio alerts', dlg); cbM = QCheckBox('Mute all', dlg)

            labels = self._audio.menu_labels()

            # Controls: [Label][Volume slider][Selection][Test]
            def make_row(lbl_text):
                lbl = QLabel(lbl_text, dlg)
                sld = QSlider(Qt.Orientation.Horizontal, dlg); sld.setRange(0,100); sld.setValue(70); sld.setFixedWidth(120)
                box = QComboBox(dlg); box.addItems(labels); box.setFixedWidth(160)  # half-ish width
                btn = QPushButton('Test', dlg); btn.setFixedWidth(80)
                return lbl, sld, box, btn

            eLbl, eSld, eBox, eTest = make_row('Edge tone:')
            pLbl, pSld, pBox, pTest = make_row('Profit tone:')
            bLbl, bSld, bBox, bTest = make_row('Both tone:')

            # Load persisted selections + volumes
            cfg = load_config()
            cbE.setChecked(bool(cfg.get('audio_enabled', True)))
            cbM.setChecked(bool(cfg.get('audio_mute_all', False)))
            eBox.setCurrentIndex(int(cfg.get('audio_edge_tone', 0)))
            pBox.setCurrentIndex(int(cfg.get('audio_profit_tone', 0)))
            bBox.setCurrentIndex(int(cfg.get('audio_both_tone', 0)))
            eSld.setValue(int(cfg.get('audio_edge_vol', 70)))
            pSld.setValue(int(cfg.get('audio_profit_vol', 70)))
            bSld.setValue(int(cfg.get('audio_both_vol', 70)))

            # Layout
            g.addWidget(cbE,0,0,1,4); g.addWidget(cbM,1,0,1,4)
            g.addWidget(eLbl,2,0); g.addWidget(eSld,2,1); g.addWidget(eBox,2,2); g.addWidget(eTest,2,3)
            g.addWidget(pLbl,3,0); g.addWidget(pSld,3,1); g.addWidget(pBox,3,2); g.addWidget(pTest,3,3)
            g.addWidget(bLbl,4,0); g.addWidget(bSld,4,1); g.addWidget(bBox,4,2); g.addWidget(bTest,4,3)

            ok = QPushButton('OK', dlg); cancel = QPushButton('Cancel', dlg)
            ok.setFixedWidth(80); cancel.setFixedWidth(80)  # match Test buttons
            g.addWidget(ok,5,2); g.addWidget(cancel,5,3)

            # Previews with volume (0..1)
            eTest.clicked.connect(lambda: self._audio.play_index(eBox.currentIndex(), eSld.value()/100.0))
            pTest.clicked.connect(lambda: self._audio.play_index(pBox.currentIndex(), pSld.value()/100.0))
            bTest.clicked.connect(lambda: self._audio.play_index(bBox.currentIndex(), bSld.value()/100.0))

            def _accept():
                c = load_config()
                c['audio_enabled'] = bool(cbE.isChecked())
                c['audio_mute_all'] = bool(cbM.isChecked())
                c['audio_edge_tone'] = int(eBox.currentIndex())
                c['audio_profit_tone'] = int(pBox.currentIndex())
                c['audio_both_tone'] = int(bBox.currentIndex())
                c['audio_edge_vol'] = int(eSld.value())
                c['audio_profit_vol'] = int(pSld.value())
                c['audio_both_vol'] = int(bSld.value())
                save_config(c)
                dlg.accept()

            ok.clicked.connect(_accept); cancel.clicked.connect(dlg.reject)
            dlg.setMinimumWidth(430); dlg.exec()
        except Exception:
            pass

    # Hook audio alerts into Table 2 flashing logic, with volumes
    def _hook_t2_audio(self):
        if getattr(self, "_t2_audio_hooked", False):
            return
        self._t2_audio_hooked = True
        orig = getattr(self, "_t2_eval_flash", None)
        if not callable(orig):
            return
        def wrapped():
            try:
                prev = dict(getattr(self, "_t2_flash_rows", {}))
                orig()
                new = getattr(self, "_t2_flash_rows", {})
                added = {r:reason for r,reason in new.items() if r not in prev}
                if not added:
                    return
                from config_loader import load_config
                cfg = load_config()
                if not cfg.get('audio_enabled', True) or cfg.get('audio_mute_all', False):
                    return
                reason = next(iter(added.values()))
                if reason == 'both':
                    idx = int(cfg.get('audio_both_tone', 0)); vol = int(cfg.get('audio_both_vol', 70))/100.0
                elif reason == 'profit':
                    idx = int(cfg.get('audio_profit_tone', 0)); vol = int(cfg.get('audio_profit_vol', 70))/100.0
                else:
                    idx = int(cfg.get('audio_edge_tone', 0)); vol = int(cfg.get('audio_edge_vol', 70))/100.0
                self._audio.play_index(idx, vol)
            except Exception:
                pass
        self._t2_eval_flash = wrapped

    DashboardClass._audio_init = _audio_init
    DashboardClass._audio_show_dialog = _audio_show_dialog
    DashboardClass._hook_t2_audio = _hook_t2_audio
    _orig = DashboardClass.__init__
    def __init__(self,*a,**k):
        _status_cb=None
        try:
            _status_cb=k.pop('status_cb') if isinstance(k,dict) and 'status_cb' in k else None
        except Exception:
            _status_cb=None
        _orig(self,*a,**k)

        try: _audio_init(self); _hook_t2_audio(self)
        except Exception: pass
    DashboardClass.__init__ = __init__
