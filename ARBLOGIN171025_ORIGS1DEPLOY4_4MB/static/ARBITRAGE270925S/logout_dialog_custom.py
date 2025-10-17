
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QWidget, QApplication
from PyQt6.QtCore import Qt

def show_logout(parent: QWidget) -> bool:
    """Return True if user clicks Yes. Styled to match the API Key dialog (black + orange)."""
    dlg = QDialog(parent)
    dlg.setWindowTitle("Logout")
    dlg.setModal(True)
    dlg.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

    # Match the API Key look: black background, orange buttons, rounded
    dlg.setStyleSheet("""
        QDialog {
            background: #0f0f0f;
            color: #e5e7eb;
            border: 1px solid #222;
            border-radius: 12px;
        }
        QLabel { color: #e5e7eb; font-size: 14px; }
        QPushButton {
            background: #ff8c2a;
            color: #111;
            border: none;
            padding: 6px 14px;
            border-radius: 10px;
            font-weight: 600;
        }
        QPushButton:hover { /* filter removed */ }
        QPushButton:disabled { background: #2a2a2a; color: #777; }
    """)

    v = QVBoxLayout(dlg)
    v.setContentsMargins(16, 16, 16, 16)
    v.setSpacing(14)

    lbl = QLabel("Exit the application?")
    v.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignLeft)

    row = QHBoxLayout()
    row.addStretch(1)

    btn_yes = QPushButton("Yes", dlg)
    btn_no = QPushButton("No", dlg)
    row.addWidget(btn_yes)
    row.addWidget(btn_no)

    v.addLayout(row)

    # Wire buttons
    clicked_yes = {"v": False}

    def _yes():
        clicked_yes["v"] = True
        dlg.accept()

    def _no():
        dlg.reject()

    btn_yes.clicked.connect(_yes)
    btn_no.clicked.connect(_no)

    # Default to "No"
    btn_no.setAutoDefault(True)
    btn_no.setDefault(True)

    # Compact size to match the Key dialog
    dlg.resize(360, 160)

    dlg.exec()
    return clicked_yes["v"]
