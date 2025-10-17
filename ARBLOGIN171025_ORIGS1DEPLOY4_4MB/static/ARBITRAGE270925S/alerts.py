class Alerts:
    def __init__(self, enabled=False, volume=0.7, preset='Silent'):
        self.enabled = bool(enabled)
        self.volume = float(volume)
        self.preset = preset
    def play_ok(self):
        return None
    def play_warn(self):
        return None
