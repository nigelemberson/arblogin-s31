# utils/export_util.py
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem

def _ts_phst():
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def _ensure_outputs():
    out = Path("outputs")
    out.mkdir(parents=True, exist_ok=True)
    return out

def export_table_to_csv(table: QTableWidget, basename: str) -> str:
    outdir = _ensure_outputs()
    csv_path = outdir / f"{basename}_{_ts_phst()}.csv"

    headers = []
    for c in range(table.columnCount()):
        item = table.horizontalHeaderItem(c)
        headers.append(item.text() if item else f"Col{c+1}")

    lines = []
    lines.append(",".join(_csv_escape(h) for h in headers))
    for r in range(table.rowCount()):
        row = []
        for c in range(table.columnCount()):
            item = table.item(r, c)
            row.append(_csv_escape(item.text() if isinstance(item, QTableWidgetItem) and item.text() else ""))
        lines.append(",".join(row))

    csv_path.write_text("\n".join(lines), encoding="utf-8")
    return str(csv_path)

def _csv_escape(s: str) -> str:
    if any(ch in s for ch in [",", "\n", '"']):
        return '"' + s.replace('"', '""') + '"'
    return s
