ARBITRAGE230925 — Part 1: Audio Purge

    Changes:
    - Removed audio-related imports, helpers, signal connections, and assets.
    - Replaced _play_ding with a no-op.
    - Added alerts.py (silent stub).
    - Scrubbed requirements.txt of audio libraries.
    - Light whitespace normalization where edits occurred.

    Note:
    - This is a checkpoint ZIP. It may still include indentation issues to be fixed in Part 2.

    Changed files:
    dashboard.py
alerts.py

    Deleted audio assets (first few):
    assets__ding.wav
ding.wav
assets/ding.wav

    Quick compile check (non-blocking):
    dashboard.py -> Sorry: IndentationError: expected an indented block after 'try' statement on line 509 (dashboard.py, line 510)
