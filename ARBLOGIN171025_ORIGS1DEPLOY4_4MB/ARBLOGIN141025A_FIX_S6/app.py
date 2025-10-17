
from flask import Flask, render_template, request, redirect, url_for, session
import os, json, hashlib, sys

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

USERS_PATHS = ["data/users.json", "users.json"]  # prefer data/users.json

def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def load_users():
    data = None
    for p in USERS_PATHS:
        data = _read_json(p)
        if data is not None:
            break
    if data is None:
        return {}

    users = {}
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                email = (k if "@" in k else v.get("email", k)).strip().lower()
                users[email] = v
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("email"):
                users[item["email"].strip().lower()] = item
    return users

def sha256_hex(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()

@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception:
        return "<h1>Landing</h1><p>Your index.html will show here in normal runs.</p>"

@app.route("/trial")
def trial():
    try:
        return render_template("trial.html")
    except Exception:
        return "<h1>Trial</h1><p>Diagnostic placeholder.</p>"

@app.route("/trial-success")
def trial_success():
    try:
        return render_template("trial_success1.html")
    except Exception:
        return "<h1>Trial Success</h1><p>Diagnostic placeholder.</p>"

# ---- GUI endpoint with logging ----
@app.route("/app")
def app_page():
    candidates = ("owner_gui.html","owner.html","app.html","dashboard.html","main.html")
    for name in candidates:
        try:
            html = render_template(name)
            print(f"[S6] /app rendering template: {name}", file=sys.stderr, flush=True)
            return html
        except Exception:
            pass
    print("[S6] /app using placeholder (no known template found).", file=sys.stderr, flush=True)
    return """
<!doctype html>
<html><head><meta charset='utf-8'><title>App</title>
<style>body{margin:0;font:16px system-ui;background:#0b1220;color:#e8f0ff;display:grid;place-items:center;height:100vh}
.card{background:#111a2b;border-radius:14px;padding:28px 32px;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,.45)}
a{color:#8fdB9a}</style></head>
<body><div class="card">
<h1>GUI App Placeholder</h1>
<p>/app is wired. Add your GUI template to /templates and we'll use it.</p>
<p><a href='""" + url_for('index') + """'>Back to Landing</a></p>
</div></body></html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        users = load_users()
        user = users.get(email)
        if user:
            stored_plain = user.get("password")
            stored_sha256 = user.get("password_hash") or user.get("sha256")
            stored_sha1 = user.get("sha1") or user.get("hash_sha1")
            stored_md5 = user.get("md5") or user.get("hash_md5")

            ok = False
            if stored_plain is not None and stored_plain == password: ok = True
            if stored_sha256 is not None and stored_sha256 == sha256_hex(password): ok = True
            if stored_sha1 is not None and stored_sha1 == hashlib.sha1(password.encode("utf-8")).hexdigest(): ok = True
            if stored_md5 is not None and stored_md5 == hashlib.md5(password.encode("utf-8")).hexdigest(): ok = True

            if ok:
                session["user"] = email
                return redirect(url_for("login_success"))
        return render_template("login.html", error="Invalid email or password")
    return render_template("login.html")

@app.route("/login/success")
def login_success():
    target = url_for("app_page")
    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Success</title>
  <style>
    body {{ margin:0; font-family:system-ui, Arial, sans-serif; background:#0c3; color:#fff; display:grid; place-items:center; height:100vh; }}
    .card {{ background:rgba(255,255,255,.12); padding:32px 40px; border-radius:14px; text-align:center; }}
    h1 {{ margin:0 0 8px 0; }}
    p {{ margin:6px 0 0 0; font-size:14px; opacity:.9; }}
    a {{ color:#fff; text-decoration:underline; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>Login Successful</h1>
    <p>Redirecting in <span id="t">5</span>…</p>
    <p><a href='{target}'>Go now</a></p>
  </div>
  <script>
    let n = 5, el = document.getElementById('t');
    const tick = setInterval(() => {{
      n -= 1; el.textContent = n;
      if (n <= 0) {{ clearInterval(tick); window.location.href = '{target}'; }}
    }}, 1000);
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
