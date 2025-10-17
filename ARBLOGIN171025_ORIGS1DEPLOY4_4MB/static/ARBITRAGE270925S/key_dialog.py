from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QApplication
from PyQt6.QtCore import Qt

BTN_QSS = """
QPushButton {
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff9a33, stop:1 #ff7a1a);
  color: #111;
  padding: 8px 14px;
  border-radius: 10px;
  border: 2px solid #d67415;
  border-top-color: #ffbe73;
  border-left-color: #ffbe73;
  font-weight: 800;
}
QPushButton:pressed {
  background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff7a1a, stop:1 #c7640f);
}
"""

DIALOG_QSS = """
QDialog { background: #161616; color: #ececec; }
QLineEdit {
  background: #0f0f0f; color:#ececec; border:1px solid #2a2a2a; border-radius:10px; padding:8px 12px;
}
"""

class KeyDialog(QDialog):
    _open_instance=None
    @classmethod
    def show_singleton(cls, parent=None, text_getter=None, text_setter=None):
        if cls._open_instance is not None:
            try:
                cls._open_instance.raise_(); cls._open_instance.activateWindow(); return cls._open_instance
            except Exception:
                cls._open_instance=None
        dlg=cls(parent, text_getter, text_setter); cls._open_instance=dlg
        dlg.finished.connect(lambda _ : setattr(cls,'_open_instance',None))
        dlg.show(); dlg.raise_(); dlg.activateWindow(); return dlg
    def __init__(self, parent=None, text_getter=None, text_setter=None):
        super().__init__(parent); self.setWindowTitle("API Key"); self.setModal(False)
        self.setStyleSheet(DIALOG_QSS)
        self.text_getter=text_getter or (lambda:""); self.text_setter=text_setter or (lambda s:None)
        v=QVBoxLayout(self); v.setContentsMargins(12,10,12,10); v.setSpacing(8)
        lab = QLabel("The Odds API Key"); lab.setAlignment(Qt.AlignmentFlag.AlignLeft); v.addWidget(lab)
        self.ed=QLineEdit(self.text_getter()); self.ed.setEchoMode(QLineEdit.EchoMode.Password); v.addWidget(self.ed)
        h=QHBoxLayout()
        btnPaste=QPushButton("Paste"); btnShow=QPushButton("Show"); btnSave=QPushButton("Save")
        for b in (btnPaste, btnShow, btnSave): b.setStyleSheet(BTN_QSS)
        btnPaste.setToolTip("Paste from clipboard (Ctrl+V)")
        h.addWidget(btnPaste); h.addWidget(btnShow); h.addWidget(btnSave); v.addLayout(h)
        # actions
        def do_paste():
            text = QApplication.clipboard().text()
            if text is None: text = ""
            self.ed.setText(text.strip())
            self.ed.setFocus(); self.ed.setCursorPosition(len(self.ed.text()))
        def toggle():
            m=self.ed.echoMode(); self.ed.setEchoMode(self.ed.EchoMode.Normal if m==self.ed.EchoMode.Password else self.ed.EchoMode.Password)
            btnShow.setText("Hide" if self.ed.echoMode()==self.ed.EchoMode.Normal else "Show")
        btnPaste.clicked.connect(do_paste)
        btnShow.clicked.connect(toggle)
        btnSave.clicked.connect(lambda: (self.text_setter(self.ed.text()), self.accept()))
