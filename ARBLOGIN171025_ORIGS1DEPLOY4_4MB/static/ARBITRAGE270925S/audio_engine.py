
from pathlib import Path
import os

SOUNDS = [
    ("Airport chime", "airport_chime.wav"),
    ("Windows notification", "windows_notify.wav"),
    ("Netflix intro", "netflix_intro.wav"),
    ("Drum hit", "drum_hit.wav"),
    ("Tambourine", "tambourine.wav"),
    ("Slot machine payout", "slot_machine.wav"),
    ("Cash register", "cash_register.wav"),
    ("Bell ring", "bell_ring.wav"),
    ("Gong", "gong.wav"),
    ("Whistle", "whistle.wav"),
    ("Horn", "horn.wav"),
    ("Click", "click.wav"),
    ("Chime", "chime.wav"),
    ("Big Ben", "big_ben.wav"),
    ("Cartoon boing", "cartoon_boing.wav"),
]

class AudioEngine:
    def __init__(self):
        # Try Qt audio first (supports volume); fallback to winsound
        try:
            from PyQt6.QtMultimedia import QSoundEffect
            from PyQt6.QtCore import QUrl
            self._Qt_QSoundEffect = QSoundEffect
            self._Qt_QUrl = QUrl
            self._effect = QSoundEffect()
            self._qt_ok = True
        except Exception:
            self._qt_ok = False
            try:
                import winsound
                self._winsound = winsound
            except Exception:
                self._winsound = None

    def _asset(self, filename: str) -> str:
        try:
            base = Path(__file__).parent
        except Exception:
            base = Path(os.getcwd())
        cand = base / "assets" / "sounds" / filename
        if cand.exists():
            return str(cand)
        cwd_cand = Path(os.getcwd()) / "assets" / "sounds" / filename
        return str(cwd_cand)

    def menu_labels(self):
        return [label for (label, fn) in SOUNDS]

    def play_index(self, idx: int, volume: float = 1.0):
        # volume: 0.0–1.0
        try:
            idx = max(0, min(len(SOUNDS)-1, int(idx)))
            fn = self._asset(SOUNDS[idx][1])
            if self._qt_ok:
                url = self._Qt_QUrl.fromLocalFile(fn)
                self._effect.setSource(url)
                try:
                    self._effect.setVolume(max(0.0, min(1.0, float(volume))))
                except Exception:
                    pass
                self._effect.play()
            elif getattr(self, "_winsound", None):
                self._winsound.PlaySound(fn, self._winsound.SND_FILENAME | self._winsound.SND_ASYNC)
        except Exception:
            pass
