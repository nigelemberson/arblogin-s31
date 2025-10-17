import json
from pathlib import Path
from typing import Any, Dict
CONFIG_PATH = Path("config.json")
DEFAULTS = {
  "title":"Sports Arbitrage Bot — Dashboard",
  "odds_api_key":"",
  "auto_copy": False,
  "ding_enabled": True,
  "ding_volume": 70,
  "ding_edge_min": 3.0,
  "ding_profit_min": 10.0
}
def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                d = DEFAULTS.copy(); d.update(data); return d
        except Exception:
            pass
    return DEFAULTS.copy()
def save_config(cfg: Dict[str, Any]) -> None:
    try:
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    except Exception:
        pass
