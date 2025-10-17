from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from datetime import datetime, timedelta, timezone
app = Flask(__name__)
# ARBLOGIN161025C S11: set secret key for session (init moved before routes)
app.secret_key = os.environ.get('SECRET_KEY', 'ARBLOGIN161025C_FALLBACK_SECRET')

import os, json
from pathlib import Path

# ARBLOGIN161025C S7: set secret key for session
import os
# === ARBLOGIN161025C S2 trial upgrade: injected routes below ===

import json, os
USERS_JSON_PATH = os.path.join(os.path.dirname(__file__), 'users.json')
def load_users():
    try:
        with open(USERS_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}
def save_users(users):
    with open(USERS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


@app.route('/trial_status')
def trial_status():
    # Returns remaining seconds for current user (trial) and whether expired
    from flask import session, jsonify
    user_email = session.get('user_email')
    # If not logged in or no user, treat as expired
    if not user_email:
        return jsonify({"remaining_seconds": 0, "expired": True})
    # Load user store
    try:
        users = load_users()
    except Exception:
        users = {}
    user = users.get(user_email) or users.get(user_email.lower())
    if not user:
        return jsonify({"remaining_seconds": 0, "expired": True})
    # Trial fields
    expires_at = user.get('trial_expires_at')
    plan = user.get('plan')
    if plan != 'trial' or not expires_at:
        # Non-trial accounts are treated as non-expired
        return jsonify({"remaining_seconds": 999999999, "expired": False})
    try:
        # expires_at stored as ISO string
        from datetime import datetime, timezone
        exp = datetime.fromisoformat(expires_at.replace('Z','+00:00'))
        now = datetime.now(timezone.utc)
        remaining = int((exp - now).total_seconds())
        if remaining < 0:
            remaining = 0
        return jsonify({"remaining_seconds": remaining, "expired": remaining == 0})
    except Exception:
        return jsonify({"remaining_seconds": 0, "expired": True})


@app.route('/subscription')
def subscription():
    
    from flask import render_template
    return render_template('subscription.html', trial_status='expired', renewal_date='—', trial_remaining='0 days')

@app.route("/__version")
def __version():
    return {"version": APP_VERSION, "folder": FOLDER_NAME}
# --------------------------------------

# ---------- Cloud-safe user storage ----------
# Scalingo allows writes in /tmp; you already set DATA_DIR=/tmp
DATA_DIR = os.environ.get("DATA_DIR", "/tmp")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

def _load_users():
    """Return a list of user dicts; create empty if file missing."""
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return list(data.values())
            return []
    except FileNotFoundError:
        return []
    except Exception:
        return []

def _save_users(users):
    """Persist users list safely to DATA_DIR."""
    try:
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
        return True
    except Exception:
        return False

def _find_user_by_email(users, email):
    email_l = (email or "").strip().lower()
    for u in users or []:
        if (u.get("email") or "").strip().lower() == email_l:
            return u
    return None
# ---------------------------------------------

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
        try:
            return render_template("free_trial.html")
        except Exception:
            return render_template("free_trial_v2.html")

    name = (request.form.get("name") or request.form.get("full_name") or "").strip()
    email = (request.form.get("email") or "").strip()
    password = (request.form.get("password") or "").strip()
    confirm = (request.form.get("confirm_password") or request.form.get("confirm") or "").strip()

    if not name or not email or not password or password != confirm:
        try:
            return render_template("free_trial.html", error="Please fill all fields and ensure passwords match.")
        except Exception:
            return render_template("free_trial_v2.html", error="Please fill all fields and ensure passwords match.")

    from datetime import datetime, timedelta, timezone
    now_iso = datetime.now(timezone.utc).isoformat()
    exp_iso = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    users = _load_users()
    if _find_user_by_email(users, email):
        try:
            return render_template("free_trial.html", error="That email already exists. Try Login.")
        except Exception:
            return render_template("free_trial_v2.html", error="That email already exists. Try Login.")

    users.append({"name": name, "full_name": name, "email": email, "password": password, "plan": "trial", "trial_started_at": now_iso, "trial_expires_at": exp_iso})
    _save_users(users)
    return redirect(url_for("trial_success"))

@app.route("/trial/success")
def trial_success():
    return render_template("trial_success1.html", redirect_to=url_for("app_page"))



@app.route("/toggle_trial", methods=["POST", "GET"])
def toggle_trial():
    # TEMP DEBUG TOOL: flip a user's trial between active (now+7d) and expired (now-1s)
    # Priority of target email: session user -> ?email param
    from flask import request, session, jsonify
    target_email = (session.get("user_email") or (request.args.get("email") or "")).strip().lower()
    mode = (request.args.get("mode") or "active").lower()
    if not target_email:
        return jsonify({"ok": False, "msg": "No target email (login first or supply ?email=)"}), 400
    try:
        users = _load_users()
        user = _find_user_by_email(users, target_email) or _find_user_by_email(users, target_email.lower())
        if not user:
            return jsonify({"ok": False, "msg": f"User not found: {target_email}"}), 404
        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)
        if mode == "expired":
            exp = (now - timedelta(seconds=1)).isoformat()
            user["plan"] = "trial"
            user["trial_started_at"] = user.get("trial_started_at") or now.isoformat()
            user["trial_expires_at"] = exp
            _save_users(users)
            return jsonify({"ok": True, "email": target_email, "mode": "expired", "trial_expires_at": exp})
        else:
            exp = (now + timedelta(days=7)).isoformat()
            user["plan"] = "trial"
            user["trial_started_at"] = now.isoformat()
            user["trial_expires_at"] = exp
            _save_users(users)
            return jsonify({"ok": True, "email": target_email, "mode": "active", "trial_expires_at": exp})
    except Exception as e:
        return jsonify({"ok": False, "msg": f"Error: {e}"}), 500

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
        session["user_email"] = email
        return redirect(url_for("login_success"))
    return render_template("login.html", error="Invalid email or password")



@app.route("/trial_expired")
def trial_expired():
    from flask import request, session
    debug = request.args.get("debug") == "1"
    server_now_utc = None
    started = None
    expires = None
    try:
        users = _load_users()
        user = _find_user_by_email(users, session.get("user_email", ""))
    except Exception:
        user = None
    if debug and user:
        try:
            from datetime import datetime, timezone
            server_now_utc = datetime.now(timezone.utc).isoformat()
            started = user.get("trial_started_at")
            expires = user.get("trial_expires_at")
        except Exception:
            pass
    return render_template("trial_expired.html", server_now_utc=server_now_utc, trial_started=started, trial_expires=expires)

@app.route("/login/success")
def login_success():
    # Decide server-side: render exactly ONE page
    from flask import session, request
    user_email = session.get("user_email")
    debug = request.args.get("debug") == "1"
    try:
        users = _load_users()
    except Exception:
        users = []
    user = _find_user_by_email(users, user_email) if user_email else None

    # Compute expiry from server UTC
    is_expired = False
    server_now_utc = None
    started = None
    expires = None
    if user:
        started = user.get("trial_started_at")
        expires = user.get("trial_expires_at")
        plan = user.get("plan")
        if plan == "trial" and expires:
            try:
                from datetime import datetime, timezone
                server_now_utc = datetime.now(timezone.utc).isoformat()
                exp_dt = datetime.fromisoformat(expires.replace("Z","+00:00"))
                now_dt = datetime.now(timezone.utc)
                is_expired = now_dt >= exp_dt
                rem = int((exp_dt - now_dt).total_seconds()) if not is_expired else 0
            except Exception:
                is_expired = True  # safest default
        else:
            # Non-trial users should proceed as active
            is_expired = False
    else:
        is_expired = True  # unknown session/user -> treat as expired

    if is_expired:
        # Render the polite expired page directly (no intermediate success page)
        return render_template("trial_expired.html",
                               trial_status='expired', remaining_seconds=0,
                               server_now_utc=server_now_utc if debug else None,
                               trial_started=started if debug else None,
                               trial_expires=expires if debug else None)
    else:
        # Render the success page (with countdown → GUI)
        return render_template("login_success2.html",
                               trial_status='active', remaining_seconds=(0 if is_expired else (rem if 'rem' in locals() else None)),
                               server_now_utc=server_now_utc if debug else None,
                               trial_started=started if debug else None,
                               trial_expires=expires if debug else None)

@app.route("/logout")
def logout():
    return redirect(url_for("index"))

if __name__ == '__main__':
    print('✅ Flask syntax OK — starting server…')
    app.run(debug=False)

@app.route("/subscription")
def subscription():
    
    from flask import render_template
    return render_template('subscription.html', trial_status='expired', renewal_date='—', trial_remaining='0 days')

@app.route("/record_subscription", methods=["POST"])
def record_subscription():
    from flask import request, jsonify, session
    data = request.get_json(silent=True) or {}
    plan = (data.get("plan") or "").strip()
    email = (session.get("user_email") or "guest").strip()
    import os, json
    path = os.path.join(os.path.dirname(__file__), "subscriptions.json")
    try:
        arr = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                arr = json.load(f)
        from datetime import datetime, timezone
        arr.append({ "email": email, "plan": plan, "timestamp": datetime.now(timezone.utc).isoformat() })
        with open(path, "w", encoding="utf-8") as f:
            json.dump(arr, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    try:
        with open(os.path.join(os.path.dirname(__file__), "subscription_audit.log"), "a", encoding="utf-8") as f:
            from datetime import datetime as _dt
            f.write(f"[{_dt.utcnow().isoformat()}Z] email={email} plan={plan}\n")
    except Exception:
        pass
    return jsonify({ "ok": True })


@app.route("/expired")
def expired():
    from flask import redirect, url_for
    return redirect(url_for('subscription'))


@app.route("/trial_used")
def trial_used():
    from flask import render_template
    return render_template('success.html', next_url='/app', delay=5, message='Trial acknowledged — entering GUI')


@app.route("/dev_toggles")
def dev_toggles():
    from flask import render_template
    return render_template('dev_toggles.html')


@app.route("/subscription")
def subscription():
    from flask import render_template
    return render_template("subscription.html",
                           trial_status="expired",
                           renewal_date="—",
                           trial_remaining="0 days")


@app.route("/checkout_demo")
def checkout_demo():
    from flask import request, render_template
    plan = request.args.get("plan","1m")
    pm = request.args.get("pm","gcash")
    msg = f"Demo only — plan: {plan}, method: {pm}. Returning to Subscription…"
    return render_template("success.html", next_url="/subscription", delay=5, message=msg)


@app.route("/pay_demo")
def pay_demo():
    from flask import request, render_template
    plan = request.args.get("plan","1m")
    pm = request.args.get("pm","gcash")
    msg = f"Payment accepted (demo). Plan: {plan}, via: {pm}. Redirecting to GUI…"
    return render_template("success.html", next_url="/app", delay=5, message=msg)
