#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parent
changed = []

def patch_dashboard(path: Path) -> bool:
    if not path.exists():
        return False
    s = path.read_text(encoding="utf-8", errors="ignore")
    orig = s

    # 1) Replace any QDialog style in inline Exit dlg to border:none and keep radius.
    s = re.sub(
        r'QDialog\s*\{[^}]*background-color:\s*#0b0f0f[^}]*\}',
        "QDialog, QDialog * { background-color: #0b0f0f; border: none; border-radius: 12px; }",
        s, flags=re.IGNORECASE|re.DOTALL
    )
    # 2) Replace dlg.resize(w,h) -> dlg.setFixedSize(360, 200)
    s = re.sub(r'dlg\.resize\(\s*\d+\s*,\s*\d+\s*\)', 'dlg.setFixedSize(360, 200)', s)
    # 3) If no fixed size after dlg creation, inject it
    if 'dlg.setFixedSize(360, 200)' not in s:
        s = re.sub(r'(dlg\s*=\s*QDialog\([^\)]*\)\s*)', r'\1\ndlg.setFixedSize(360, 200)\n', s)

    if s != orig:
        path.write_text(s, encoding="utf-8")
        return True
    return False

def patch_exit_custom(path: Path) -> bool:
    if not path.exists():
        return False
    s = path.read_text(encoding="utf-8", errors="ignore")
    orig = s

    # Enforce size
    if 'setFixedSize(' in s:
        s = re.sub(r'setFixedSize\(\s*\d+\s*,\s*\d+\s*\)', 'setFixedSize(360, 200)', s)
    else:
        s = re.sub(
            r'(class\s+ExitDialog\([^\)]*\)\s*:\s*.*?def\s+__init__\([^\)]*\):\s*.*?super\(\)\.__init__\([^\)]*\)\s*)',
            r'\1\n        self.setFixedSize(360, 200)\n',
            s, flags=re.DOTALL
        )

    # Replace/add stylesheet
    if 'setStyleSheet' in s:
        s = re.sub(
            r'setStyleSheet\(\s*r?["\'].*?["\']\s*\)',
            'setStyleSheet("QDialog, QDialog * { background-color: #0b0f0f; border: none; } '
            'QLabel { color: #e6e6e6; font-size: 14px; } '
            'QPushButton { background: #ff8c2a; color: #111; font-weight: 700; border-radius: 10px; padding: 8px 18px; } '
            'QPushButton:hover { background: #ffa64d; } '
            'QPushButton:pressed { background: #ff7a00; }")',
            s, flags=re.DOTALL
        )
    else:
        s = re.sub(
            r'(class\s+ExitDialog\([^\)]*\)\s*:\s*.*?def\s+__init__\([^\)]*\):\s*.*?super\(\)\.__init__\([^\)]*\)\s*)',
            r'\1\n        self.setStyleSheet("QDialog, QDialog * { background-color: #0b0f0f; border: none; } '
            'QLabel { color: #e6e6e6; font-size: 14px; } '
            'QPushButton { background: #ff8c2a; color: #111; font-weight: 700; border-radius: 10px; padding: 8px 18px; } '
            'QPushButton:hover { background: #ffa64d; } '
            'QPushButton:pressed { background: #ff7a00; }")\n',
            s, flags=re.DOTALL
        )

    if s != orig:
        path.write_text(s, encoding="utf-8")
        return True
    return False

def main():
    dash = ROOT / "dashboard.py"
    exitc = ROOT / "exit_dialog_custom.py"

    c1 = patch_dashboard(dash)
    c2 = patch_exit_custom(exitc)

    print("Patched files:")
    if c1: print(" - dashboard.py")
    if c2: print(" - exit_dialog_custom.py")
    if not (c1 or c2):
        print(" (nothing changed — patterns not found)")

if __name__ == "__main__":
    main()
