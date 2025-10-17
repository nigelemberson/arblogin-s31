from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from pathlib import Path

app = Flask(__name__, static_url_path="/static")
# --- version + folder (clean S12) ---
APP_VERSION = "ARBLOGIN151025A_S15"
import pathlib as _pl
FOLDER_NAME = _pl.Path(__file__).resolve().parent.name
try:
    app.jinja_env.globals['APP_VERSION'] = APP_VERSION
    app.jinja_env.globals['FOLDER_NAME'] = FOLDER_NAME
except Exception:
    pass

@app.route("/__version")
def __version():
    return {"version": APP_VERSION, "folder": FOLDER_NAME}
# --- end injected ---

# --- injected: centralized version and folder name ---
# Determine current folder name dynamically
import pathlib as _pl
FOLDER_NAME = _pl.Path(__file__).resolve().parent.name

# Expose to Jinja templates
try:
    app.jinja_env.globals['APP_VERSION'] = APP_VERSION
    app.jinja_env.globals['FOLDER_NAME'] = FOLDER_NAME
except Exception:
    pass


@app.route("/")
def index():
    # Pin the landing to landing_bc.html (no guessing)
    return render_template("landing_bc.html")


@app.route("/app")
def app_page():
    # Prefer your main GUI template name, with a gentle fallback
    try:
        return render_template("app_dashboard.html")
    except Exception:
        return render_template("app.html")


@app.route("/trial", methods=["GET", "POST"])
def trial():
    if request.method == "GET":
        # Show your existing free-trial form (v2 or v1); prefer v2
        try:
            return render_template("free_trial.html")
        except Exception:
            return render_template("free_trial_v2.html")
    # POST: create account
    name = (request.form.get("name") or request.form.get("full_name") or "").strip()
    email = (request.form.get("email") or "").strip()
    password = (request.form.get("password") or "").strip()
    confirm = (request.form.get("confirm_password") or request.form.get("confirm") or "").strip()

    # Basic validation
    if not name or not email or not password or password != confirm:
        # Re-render form with a simple message (your form may display it)
        try:
            return render_template("free_trial.html", error="Please fill in all fields and ensure passwords match.")
        except Exception:
            return render_template("free_trial_v2.html", error="Please fill in all fields and ensure passwords match.")

    users = _load_users()
    if _find_user_by_email(users, email):
        # Already exists
        try:
            return render_template("free_trial.html", error="That email already exists. Try Login.")
        except Exception:
            return render_template("free_trial_v2.html", error="That email already exists. Try Login.")

    # Store plain password as requested (no hashes)
    users.append({
        "name": name,
        "full_name": name,
        "email": email,
        "password": password
    })
    _save_users(users)

    # Success screen with 5s redirect to /app
    return redirect(url_for("trial_success"))


@app.route("/trial/success")
def trial_success():
    # Template performs a 5-second redirect to /app
    return render_template("trial_success1.html", redirect_to=url_for("app_page"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = (request.form.get("email") or "").strip()
    pw = (request.form.get("password") or "").strip()
    if not email or not pw:
        # Fall back to same template with a simple error message
        return render_template("login.html", error="Invalid email or password")

    users = _load_users()
    user = _find_user_by_email(users, email)

    # Accept plain passwords; if record has password_hash, we still won't use it
    if user and user.get("password") == pw:
        return redirect(url_for("login_success"))

    # Else fail
    return render_template("login.html", error="Invalid email or password")


@app.route("/login/success")
def login_success():
    # Template performs a 5-second redirect to /app
    return render_template("login_success2.html", redirect_to=url_for("app_page"))


@app.route("/logout")
def logout():
    # No session management here; simply send back to landing
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=False)


