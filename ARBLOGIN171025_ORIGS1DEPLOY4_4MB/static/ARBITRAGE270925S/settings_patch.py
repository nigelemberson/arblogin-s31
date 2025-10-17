from PyQt6.QtWidgets import QWidget, QDialog, QPushButton, QLabel, QFormLayout, QDoubleSpinBox, QSpinBox, QApplication, QCheckBox, QSlider
from PyQt6.QtCore import QObject, QEvent
EDGE_LABELS=['edge ≥ %','edge >= %','edge %','edge']
PROFIT_LABELS=['profit ≥ £','profit >= £','profit £','profit']
def _norm(s): return (s or '').strip().lower()
def apply(DashboardClass):
    def _app_dir(self):
        try:
            import __main__, os
            p=getattr(__main__,'__file__',None)
            return os.path.abspath(os.path.dirname(p)) if p else os.getcwd()
        except Exception:
            import os; return os.getcwd()
    def _cfg_path(self):
        import os; return os.path.join(_app_dir(self),'config.json')
    def _ensure_cfg(self):
        if not hasattr(self,'cfg') or not isinstance(self.cfg,dict): self.cfg={}
    def _load_cfg(self):
        _ensure_cfg(self)
        try:
            from config_loader import load_config as _m; _m(self)
        except Exception:
            import json, os
            p=_cfg_path(self)
            if os.path.exists(p):
                with open(p,'r',encoding='utf-8') as f: self.cfg=json.load(f) or self.cfg
        self.cfg.setdefault('ding_edge_min', float(self.cfg.get('ding_edge_min',3.0)))
        self.cfg.setdefault('ding_profit_min', float(self.cfg.get('ding_profit_min',10.0)))
    def _save_cfg(self):
        _ensure_cfg(self)
        try:
            from config_loader import save_config as _m; _m(self.cfg); return
        except Exception:
            import json, os
            with open(_cfg_path(self),'w',encoding='utf-8') as f: json.dump(self.cfg,f,indent=2,ensure_ascii=False)
    def _get_thresholds(self):
        _ensure_cfg(self)
        try: return float(self.cfg.get('ding_edge_min',3.0)), float(self.cfg.get('ding_profit_min',10.0))
        except Exception: return 3.0, 10.0
    def _set_thresholds(self, edge=None, profit=None, persist=True):
        _ensure_cfg(self); changed=False
        if edge is not None:
            try: edge=float(edge); self.cfg['ding_edge_min']=edge; self.ding_edge_min=edge; changed=True
            except Exception: pass
        if profit is not None:
            try: profit=float(profit); self.cfg['ding_profit_min']=profit; self.ding_profit_min=profit; changed=True
            except Exception: pass
        if persist and changed: _save_cfg(self)
        try: self._t2_eval_flash()
        except Exception: pass
    def _hide_legacy(root):
        try:
            for cb in root.findChildren(QCheckBox):
                if _norm(cb.text()).startswith('enable ding'): cb.setVisible(False)
            for b in root.findChildren(QPushButton):
                if _norm(b.text()) in ('test ding',): b.setVisible(False)
            for sl in root.findChildren(QSlider): sl.setVisible(False)
        except Exception: pass
    def _is_settings_dialog(obj):
        try:
            if isinstance(obj,QDialog) and _norm(getattr(obj,'windowTitle',lambda:'')())=='settings': return True
        except Exception: pass
        try:
            labels=[_norm(w.text()) for w in obj.findChildren(QLabel)]
            if any(l in EDGE_LABELS for l in labels) and any(l in PROFIT_LABELS for l in labels): return True
        except Exception: pass
        return False
    def _bind_settings(self, root: QWidget=None):
        root=root or self
        if not _is_settings_dialog(root): return
        _hide_legacy(root)
        edge_widgets=[]; profit_widgets=[]
        for form in root.findChildren(QFormLayout):
            rows=form.rowCount()
            for r in range(rows):
                li=form.itemAt(r, QFormLayout.ItemRole.LabelRole)
                fi=form.itemAt(r, QFormLayout.ItemRole.FieldRole)
                lbl=li.widget() if li else None; fld=fi.widget() if fi else None
                if isinstance(lbl, QLabel) and hasattr(fld,'value') and hasattr(fld,'setValue'):
                    t=_norm(lbl.text())
                    if t in EDGE_LABELS: edge_widgets.append(fld)
                    if t in PROFIT_LABELS: profit_widgets.append(fld)
        if not edge_widgets or not profit_widgets:
            cands=[w for w in root.findChildren(QWidget) if hasattr(w,'value') and hasattr(w,'setValue')]
            if len(cands)>=2:
                if not edge_widgets: edge_widgets=[cands[0]]
                if not profit_widgets: profit_widgets=[cands[1]]
        e,p=_get_thresholds(self)
        for w in edge_widgets:
            try: w.blockSignals(True); w.setValue(e); w.blockSignals(False)
            except Exception: pass
            try:
                if not w.property('bound_edge'):
                    w.valueChanged.connect(lambda v, _w=w: _set_thresholds(self, edge=v, profit=None, persist=True))
                    try: w.editingFinished.connect(lambda _w=w: _set_thresholds(self, edge=_w.value(), profit=None, persist=True))
                    except Exception: pass
                    w.setProperty('bound_edge', True)
            except Exception: pass
        for w in profit_widgets:
            try: w.blockSignals(True); w.setValue(p); w.blockSignals(False)
            except Exception: pass
            try:
                if not w.property('bound_profit'):
                    w.valueChanged.connect(lambda v, _w=w: _set_thresholds(self, edge=None, profit=v, persist=True))
                    try: w.editingFinished.connect(lambda _w=w: _set_thresholds(self, edge=None, profit=_w.value(), persist=True))
                    except Exception: pass
                    w.setProperty('bound_profit', True)
            except Exception: pass
        if isinstance(root, QDialog):
            def _persist_close(*a):
                try: self._save_from(root)
                except Exception: pass
            try: root.finished.connect(_persist_close)
            except Exception: pass
    def _save_from(self, root: QWidget):
        if not _is_settings_dialog(root): return
        edge_v=None; profit_v=None
        for form in root.findChildren(QFormLayout):
            rows=form.rowCount()
            for r in range(rows):
                li=form.itemAt(r, QFormLayout.ItemRole.LabelRole)
                fi=form.itemAt(r, QFormLayout.ItemRole.FieldRole)
                lbl=li.widget() if li else None; fld=fi.widget() if fi else None
                if isinstance(lbl, QLabel) and hasattr(fld,'value'):
                    t=_norm(lbl.text())
                    if edge_v is None and t in EDGE_LABELS: edge_v=fld.value()
                    if profit_v is None and t in PROFIT_LABELS: profit_v=fld.value()
        if edge_v is None or profit_v is None:
            cands=[w for w in root.findChildren(QWidget) if hasattr(w,'value')]
            if edge_v is None and len(cands)>=1: edge_v=cands[0].value()
            if profit_v is None and len(cands)>=2: profit_v=cands[1].value()
        _set_thresholds(self, edge=edge_v, profit=profit_v, persist=True)
    DashboardClass._load_cfg=_load_cfg; DashboardClass._save_cfg=_save_cfg
    DashboardClass._get_thresholds=_get_thresholds; DashboardClass._set_thresholds=_set_thresholds
    DashboardClass._bind_settings=_bind_settings; DashboardClass._save_from=_save_from
    _o=DashboardClass.__init__
    def __init__(self,*a,**k):
        _status_cb=None
        try:
            _status_cb=k.pop('status_cb') if isinstance(k,dict) and 'status_cb' in k else None
        except Exception:
            _status_cb=None
        _o(self,*a,**k)
        try:
            if callable(_status_cb): setattr(self,'status_cb',_status_cb)
        except Exception:
            pass

        try: _load_cfg(self)
        except Exception: pass
        app=QApplication.instance()
        if app and not hasattr(self,'_settings_binder'):
            class _Binder(QObject):
                def __init__(self, owner): super().__init__(owner); self._o=owner
                def eventFilter(self,obj,ev):
                    try:
                        if ev.type()==QEvent.Show and isinstance(obj, QWidget) and _is_settings_dialog(obj):
                            try: self._o._bind_settings(obj)
                            except Exception: pass
                    except Exception: pass
                    return False
            self._settings_binder=_Binder(self); app.installEventFilter(self._settings_binder)
    DashboardClass.__init__=__init__
