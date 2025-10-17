
from flask import Flask, render_template, request, redirect, url_for
import json, os
from pathlib import Path

app = Flask(__name__, static_url_path="/static")

# ---------- Version + folder (S16) ----------
APP_VERSION = "ARBLOGIN151025A_S16"
FOLDER_NAME = Path(__file__).resolve().parent.name
try:
    app.jinja_env.globals['APP_VERSION'] = APP_VERSION
    app.jinja_env.globals['FOLDER_NAME'] = FOLDER_NAME
except Exception:
    pass

@app.route("/__version")
def __version():
    return {"version": APP_VERSION, "folder": FOLDER_NAME}
# --------------------------------------------

# ---------- User storage helpers (permanent) ----------
DATA_DIR = os.environ.get("DATA_DIR", "/tmp")  # Scalingo-safe writable dir
USERS_PATH = os.path.join(DATA_DIR, "users.json")

def _load_users():
    """
    Returns a list of user dicts: [{name, email, password}, ...]
    Missing/invalid file -> returns [].
    """
    try:
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            # legacy dict storage -> convert to list if needed
            if isinstance(data, dict):
                return list(data.values())
            return []
    except FileNotFoundError:
        return []
    except Exception as e:
        print("User load error:", e)
        return []

def _save_users(users):
    """Safely write the users list."""
    try:
        os.makedirs(os.path.dirname(USERS_PATH), exist_ok=True)
        with open(USERS_PATH, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
        return True
    except Exception as e:
        print("User save error:", e)
        return False

def _find_user_by_email(users, email):
    email_l = (email or "").strip().lower()
    for u in users or []:
        if (u.get("email") or "").strip().lower() == email_l:
            return u
    return None
# ------------------------------------------------------

@app.route("/")
def index():
    return render_template("landing_bc.html")

@app.route("/app")
def app_page():
    try:
        return render_template("app_dashboard.html")
    except Exception:
        return render_template("app.html")

@app.route("/trial", methods=["GET", "POST"])
def trial():
    if request.method == "GET":
        # Prefer your existing free-trial form; try both names
        try:
            return render_template("free_trial.html")
        except Exception:
            return render_template("free_trial_v2.html")

    # POST: create account
    name = (request.form.get("name") or request.form.get("full_name") or "").strip()
    email = (request.form.get("email") or "").strip()
    password = (request.form.get("password") or "").strip()
    confirm = (request.form.get("confirm_password") or request.form.get("confirm") or "").strip()

    if not name or not email or not password or password != confirm:
        try:
            return render_template("free_trial.html", error="Please fill in all fields and ensure passwords match.")
        except Exception:
            return render_template("free_trial_v2.html", error="Please fill in all fields and ensure passwords match.")

    users = _load_users()
    if _find_user_by_email(users, email):
        try:
            return render_template("free_trial.html", error="That email already exists. Try Login.")
        except Exception:
            return render_template("free_trial_v2.html", error="That email already exists. Try Login.")

    users.append({"name": name, "full_name": name, "email": email, "password": password})
    _save_users(users)
    return redirect(url_for("trial_success"))

@app.route("/trial/success")
def trial_success():
    # Template should redirect to /app; server side just renders it
    return render_template("trial_success1.html", redirect_to=url_for("app_page"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = (request.form.get("email") or "").strip()
    pw = (request.form.get("password") or "").strip()
    if not email or not pw:
        return render_template("login.html", error="Invalid email or password")

    users = _load_users()
    user = _find_user_by_email(users, email)
    if user and user.get("password") == pw:
        return redirect(url_for("login_success"))
    return render_template("login.html", error="Invalid email or password")

@app.route("/login/success")
def login_success():
    return render_template("login_success2.html", redirect_to=url_for("app_page"))

@app.route("/logout")
def logout():
    return redirect(url_for("index"))

if __name__ == "__main__":
    # Keep debug False in production
    app.run(debug=False)
