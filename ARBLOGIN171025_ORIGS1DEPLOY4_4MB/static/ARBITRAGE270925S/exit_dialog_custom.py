
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont

DIALOG_QSS = (
    "QDialog, QDialog * { background-color: #0b0f0f; border: none !important; outline: none; }"
    " QLabel#title { color: #1aff97; font-weight: 800; }"
    " QLabel#body { color: #e6e6e6; }"
    " QPushButton { background: #ff8c2a; color: #111; font-weight: 700; border-radius: 10px; padding: 6px 12px; }"
    " QPushButton:hover { background: #ffa64d; }"
    " QPushButton:pressed { background: #ff7a00; }"
)

class ExitDialog(QDialog):
    def __init__(self, parent=None, accent_color=None, body_font=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Confirm Exit")
        self.setFixedSize(224, 133)

        # Apply local style; swap in the exact accent green if provided
        style = DIALOG_QSS if not accent_color else DIALOG_QSS.replace("#1aff97", str(accent_color))
        self.setStyleSheet(style)

        v = QVBoxLayout(self); v.setContentsMargins(12, 10, 12, 10); v.setSpacing(8)

        lblTitle = QLabel("Exit Application", self); lblTitle.setObjectName("title")
        lblMsg = QLabel("Are you sure you want to exit the application?", self); lblMsg.setObjectName("body")
        lblMsg.setWordWrap(True)

        if body_font is not None:
            # Use the same font/size as the Table 1 cells for the message
            lblMsg.setFont(body_font)
            # Title uses the same family but bold
            f = QFont(body_font); f.setBold(True); lblTitle.setFont(f)

        v.addWidget(lblTitle); v.addWidget(lblMsg)

        row = QHBoxLayout(); row.addStretch(1)
        btnYes = QPushButton("Yes", self); btnNo = QPushButton("No", self)
        btnYes.clicked.connect(self.accept); btnNo.clicked.connect(self.reject)
        row.addWidget(btnYes); row.addWidget(btnNo)
        v.addLayout(row)
