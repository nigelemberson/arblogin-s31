
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QBoxLayout, QSizePolicy
def apply(DashboardClass):
    _orig=DashboardClass.__init__
    def __init__(self,*a,**k):
        _status_cb=None
        try:
            _status_cb=k.pop('status_cb') if isinstance(k,dict) and 'status_cb' in k else None
        except Exception:
            _status_cb=None
        _orig(self,*a,**k)

        try:
            if getattr(self,'_audio_btn',None) is None:
                self._audio_btn=QPushButton('Audio', self)
                try: self._audio_btn.clicked.connect(lambda: getattr(self,'_audio_show_dialog')())
                except Exception: pass
                settings_btn=None
                for b in self.findChildren(QPushButton):
                    if (b.text() or '').strip().lower()=='settings': settings_btn=b; break
                inserted=False
                if settings_btn:
                    # match style & size
                    try: self._audio_btn.setStyleSheet(settings_btn.styleSheet())
                    except Exception: pass
                    try: self._audio_btn.setSizePolicy(settings_btn.sizePolicy())
                    except Exception: self._audio_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                    parent=settings_btn.parentWidget(); lay=parent.layout() if parent else None
                    if isinstance(lay,(QVBoxLayout,QHBoxLayout,QBoxLayout)):
                        idx=-1
                        for i in range(lay.count()):
                            w=lay.itemAt(i).widget()
                            if w is settings_btn: idx=i; break
                        if idx>=0:
                            lay.insertWidget(max(0,idx-1), self._audio_btn); inserted=True
                if not inserted:
                    rootlay=self.layout()
                    if isinstance(rootlay, QBoxLayout): rootlay.insertWidget(0, self._audio_btn)
        except Exception: pass
    DashboardClass.__init__=__init__
