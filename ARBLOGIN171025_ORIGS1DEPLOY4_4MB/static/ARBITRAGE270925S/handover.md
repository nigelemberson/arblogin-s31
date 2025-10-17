## D — Alerts adapter (stub) + wiring
- Added alerts.py with Alerts(enabled=False) default (no sound).
- Wired `self.alerts` in Dashboard.__init__.
- Added safe start_dashboard.py that disables any legacy audio hooks.
