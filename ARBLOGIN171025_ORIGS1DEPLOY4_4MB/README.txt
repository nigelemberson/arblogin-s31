UPDATE S4 — Plain-Password Login (Local)

Files in this package:
- app.py      → drop into your ARBLOGIN141025A folder (replace the old file).
- README.txt  → this file.

Expected templates that must already exist under ARBLOGIN141025A/templates/ :
  landing_bc.html   (for /)
  free_trial.html   (for /trial)
  login.html        (for /login form)
  app_dashboard.html (for /app GUI)

Expected users file:
  ARBLOGIN141025A/data/users.json
  Example entry format (plaintext password):
  [
    {"full_name": "n", "email": "n@n", "password": "n"}
  ]

How to run (PowerShell from ARBLOGIN141025A):
  $env:FLASK_APP="app.py"
  python -m flask run

What this build does:
  /       → landing_bc.html
  /trial  → free_trial.html
  /login  → login.html (POST checks plaintext "password" in data/users.json)
  /app    → app_dashboard.html
  /logout → redirects to /

If any of those templates have different filenames on your machine,
tell me the exact names and I’ll send a tiny update pointing to them.
