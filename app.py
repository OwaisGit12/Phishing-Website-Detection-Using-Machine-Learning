# app.py
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import joblib
import pandas as pd
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
import secrets
import smtplib
from email.mime.text import MIMEText
from functools import wraps
import time

# -------------------------
# CONFIG
# -------------------------
app = Flask(__name__)
app.secret_key = "Ajsd8723nNsd89@!33JKSJhhs77HHkss9921LLL"   # For local use; use env var in prod
app.permanent_session_lifetime = timedelta(days=7)  # used when "Remember me" checked

USERS_FILE = "users.json"
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 60     # max requests per IP per window

# SMTP (optional)
SMTP_HOST = ""
SMTP_PORT = 587
SMTP_USER = ""
SMTP_PASS = ""
EMAIL_FROM = "no-reply@example.com"

# -------------------------
# ADMIN CREDENTIALS - EDIT THESE
# -------------------------
ADMIN_USERNAME = "admin"
# Generate a hash with: generate_password_hash("your_admin_password")
# Example: ADMIN_PASSWORD_HASH = generate_password_hash("admin123")
# Paste the hash string below or create one programmatically.
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")  # change "admin123" before production

# -------------------------
# Load ML model
# -------------------------
model = joblib.load('model.pkl')
FEATURE_COLUMNS = [
    'Have_IP', 'Have_At', 'URL_Length', 'URL_Depth', 'Redirection', 'https_Domain',
    'TinyURL', 'Prefix/Suffix', 'DNS_Record', 'Web_Traffic', 'Domain_Age',
    'Domain_End', 'iFrame', 'Mouse_Over', 'Right_Click', 'Web_Forwards'
]

def extract_features(url):
    return {
        'Have_IP': 1 if any(char.isdigit() for char in url) else -1,
        'Have_At': 1 if '@' in url else -1,
        'URL_Length': len(url),
        'URL_Depth': url.count('/'),
        'Redirection': 1 if '//' in url[7:] else -1,
        'https_Domain': 1 if 'https' in url else -1,
        'TinyURL': 1 if 'bit.ly' in url or 'tinyurl' in url else -1,
        'Prefix/Suffix': 1 if '-' in url else -1,
        'DNS_RECORD': 1,
        'DNS_Record': 1,
        'Web_Traffic': 1,
        'Domain_Age': 1,
        'Domain_End': 1,
        'iFrame': 1,
        'Mouse_Over': 1,
        'Right_Click': 1,
        'Web_Forwards': 1
    }

# -------------------------
# USER / FILE UTIL
# -------------------------
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2, default=str)

# -------------------------
# SIMPLE RATE LIMIT (in-memory)
# -------------------------
rate_table = {}  # ip -> [timestamps]

def rate_limited(ip):
    now = time.time()
    arr = rate_table.get(ip, [])
    # remove old
    arr = [t for t in arr if t > now - RATE_LIMIT_WINDOW]
    arr.append(now)
    rate_table[ip] = arr
    return len(arr) > RATE_LIMIT_MAX

# -------------------------
# EMAIL HELPERS (optional)
# -------------------------
def send_email(to_email, subject, body):
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        print("SMTP not configured. Skipping email send. Subject:", subject)
        return False
    try:
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = to_email
        s = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.sendmail(EMAIL_FROM, [to_email], msg.as_string())
        s.quit()
        return True
    except Exception as e:
        print("Email send error:", e)
        return False

# -------------------------
# AUTH DECORATORS
# -------------------------
def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return wrapped

# -------------------------
# ROUTES (Auth, Register, Login, Home)
# -------------------------
@app.route("/")
def login():
    if "user" in session:
        return redirect("/home")
    a = secrets.randbelow(10) + 1
    b = secrets.randbelow(10) + 1
    session['captcha'] = f"{a}+{b}"
    return render_template("login.html", captcha_question=f"{a} + {b} = ?")

@app.route("/register")
def register():
    if "user" in session:
        return redirect("/home")
    a = secrets.randbelow(10) + 1
    b = secrets.randbelow(10) + 1
    session['captcha'] = f"{a}+{b}"
    return render_template("register.html", captcha_question=f"{a} + {b} = ?")

@app.route("/do_register", methods=["POST"])
def do_register():
    ip = request.remote_addr
    if rate_limited(ip):
        return "Too many requests. Try later.", 429

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    email = request.form.get("email", "").strip().lower()
    captcha = request.form.get("captcha", "").strip()

    if len(username) < 3 or len(password) < 6:
        return "Username must be >=3 chars and password >=6 chars", 400

    expected = session.get('captcha', '')
    try:
        if expected and str(eval(expected)) != captcha:
            return "CAPTCHA incorrect", 400
    except:
        return "CAPTCHA error", 400

    users = load_users()
    if username in users:
        return "Username already exists", 400

    hashed = generate_password_hash(password)
    users[username] = {
        "password": hashed,
        "email": email,
        "verified": False if email else True,
        "verify_token": None,
        "reset_token": None,
        "reset_expiry": None,
        "scans": []
    }

    if email:
        token = str(uuid.uuid4())
        users[username]["verify_token"] = token
        link = url_for("verify_email", token=token, _external=True)
        body = f"Hi {username},<br><br>Click to verify: <a href='{link}'>{link}</a>"
        send_email(email, "Verify your account", body)

    save_users(users)
    return redirect("/")

@app.route("/do_login", methods=["POST"])
def do_login():
    ip = request.remote_addr
    if rate_limited(ip):
        return "Too many requests. Try later.", 429

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    remember = request.form.get("remember") == "on"
    captcha = request.form.get("captcha", "").strip()

    expected = session.get('captcha', '')
    try:
        if expected and str(eval(expected)) != captcha:
            return "CAPTCHA incorrect", 400
    except:
        return "CAPTCHA error", 400

    users = load_users()
    if username not in users or not check_password_hash(users[username]["password"], password):
        return "Invalid credentials", 401

    if not users[username].get("verified", True):
        return "Please verify your email before logging in.", 403

    session["user"] = username
    session["is_admin"] = False
    if remember:
        session.permanent = True
    else:
        session.permanent = False
    return redirect("/home")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -------------------------
# HOME / PREDICT (AJAX)
# -------------------------
@app.route("/home")
@login_required
def home():
    users = load_users()
    user = users.get(session["user"], {})
    return render_template("index.html", url="", prediction_text=None, scans=user.get("scans", []))

@app.route("/predict", methods=["POST"])
@login_required
def predict():
    ip = request.remote_addr
    if rate_limited(ip):
        return jsonify({"error": "Too many requests"}), 429

    if request.is_json:
        data = request.get_json()
        url = data.get("url", "")
    else:
        url = request.form.get("url", "")

    if not url:
        return jsonify({"error": "URL required"}), 400

    features = extract_features(url)
    X = pd.DataFrame([[features[col] for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
    prediction = model.predict(X)[0]
    label = "Phishing" if int(prediction) == 1 else "Legitimate"
    text = f"Prediction: {label}"

    users = load_users()
    username = session["user"]
    user = users.get(username)
    if user is not None:
        entry = {
            "id": str(uuid.uuid4()),
            "url": url,
            "result": label,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        user.setdefault("scans", [])
        user["scans"].insert(0, entry)
        user["scans"] = user["scans"][:200]
        save_users(users)

    if request.is_json:
        return jsonify({"prediction_text": text, "label": label})
    return render_template("index.html", prediction_text=text, url=url, scans=user.get("scans", []))

# -------------------------
# DELETE / CLEAR SCANS (user)
# -------------------------
@app.route("/delete_scan", methods=["POST"])
@login_required
def delete_scan():
    data = request.get_json() or {}
    scan_id = data.get("scan_id")
    if not scan_id:
        return jsonify({"error": "scan_id required"}), 400

    users = load_users()
    username = session["user"]
    user = users.get(username)
    if not user:
        return jsonify({"error": "user not found"}), 404

    original = len(user.get("scans", []))
    user["scans"] = [s for s in user.get("scans", []) if s.get("id") != scan_id]
    if len(user["scans"]) == original:
        return jsonify({"error": "scan not found"}), 404

    save_users(users)
    return jsonify({"ok": True})

@app.route("/clear_scans", methods=["POST"])
@login_required
def clear_scans():
    users = load_users()
    username = session["user"]
    user = users.get(username)
    if not user:
        return jsonify({"error": "user not found"}), 404
    user["scans"] = []
    save_users(users)
    return jsonify({"ok": True})

# -------------------------
# ADMIN: login / dashboard / actions
# -------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        if session.get("is_admin"):
            return redirect(url_for("admin_dashboard"))
        return render_template("admin_login.html")
    # POST
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if username != ADMIN_USERNAME or not check_password_hash(ADMIN_PASSWORD_HASH, password):
        return "Invalid admin credentials", 401
    session["is_admin"] = True
    session["user"] = ADMIN_USERNAME  # optional convenience
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    session.pop("user", None)
    return redirect(url_for("admin_login"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    users = load_users()
    # render a page listing users and their scans
    return render_template("admin_dashboard.html", users=users)

# Admin can delete any user's single scan
@app.route("/admin/delete_scan", methods=["POST"])
@admin_required
def admin_delete_scan():
    data = request.get_json() or {}
    target_user = data.get("username")
    scan_id = data.get("scan_id")
    if not target_user or not scan_id:
        return jsonify({"error":"username and scan_id required"}), 400
    users = load_users()
    if target_user not in users:
        return jsonify({"error":"user not found"}), 404
    user = users[target_user]
    original = len(user.get("scans", []))
    user["scans"] = [s for s in user.get("scans", []) if s.get("id") != scan_id]
    if len(user["scans"]) == original:
        return jsonify({"error":"scan not found"}), 404
    save_users(users)
    return jsonify({"ok": True})

# Admin can clear all scans of a user
@app.route("/admin/clear_user_scans", methods=["POST"])
@admin_required
def admin_clear_user_scans():
    data = request.get_json() or {}
    target_user = data.get("username")
    if not target_user:
        return jsonify({"error":"username required"}), 400
    users = load_users()
    if target_user not in users:
        return jsonify({"error":"user not found"}), 404
    users[target_user]["scans"] = []
    save_users(users)
    return jsonify({"ok": True})

# -------------------------
# EMAIL VERIFY + PASSWORD RESET (same as before)
# -------------------------
@app.route("/verify/<token>")
def verify_email(token):
    users = load_users()
    for uname, data in users.items():
        if data.get("verify_token") == token:
            users[uname]["verified"] = True
            users[uname]["verify_token"] = None
            save_users(users)
            return f"Email verified for {uname}. You may now <a href='/'>login</a>."
    return "Invalid or expired verification link."

@app.route("/request_reset", methods=["GET", "POST"])
def request_reset():
    if request.method == "GET":
        return render_template("request_reset.html")
    email = request.form.get("email", "").strip().lower()
    users = load_users()
    matched = None
    for uname, data in users.items():
        if data.get("email", "").lower() == email:
            matched = uname
            break
    if not matched:
        return "If an account with that email exists, a reset link was sent."
    token = str(uuid.uuid4())
    users[matched]["reset_token"] = token
    users[matched]["reset_expiry"] = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    save_users(users)
    link = url_for("reset_with_token", token=token, _external=True)
    body = f"Click to reset your password: <a href='{link}'>{link}</a><br>This link expires in 1 hour."
    send_email(email, "Password reset — Phishing Detector", body)
    return "If an account with that email exists, a reset link was sent."

@app.route("/reset/<token>", methods=["GET", "POST"])
def reset_with_token(token):
    users = load_users()
    username = None
    for uname, data in users.items():
        if data.get("reset_token") == token:
            try:
                expiry = datetime.fromisoformat(data.get("reset_expiry"))
            except:
                expiry = datetime.utcnow() - timedelta(hours=1)
            if datetime.utcnow() > expiry:
                return "Reset link expired."
            username = uname
            break
    if not username:
        return "Invalid or expired reset token."

    if request.method == "GET":
        return render_template("reset_password.html", token=token)
    newpass = request.form.get("password", "")
    if len(newpass) < 6:
        return "Password too short", 400
    users[username]["password"] = generate_password_hash(newpass)
    users[username]["reset_token"] = None
    users[username]["reset_expiry"] = None
    save_users(users)
    return "Password updated. You can now <a href='/'>login</a>."

# -------------------------
# DEV: quick route to view users (comment out in prod)
# -------------------------
@app.route("/_debug_users")
@admin_required
def debug_users():
    return jsonify(load_users())

if __name__ == '__main__':
    app.run(debug=True, port=5000)

@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    msg = data.get("msg")

    # If SMTP configured → send mail
    if SMTP_USER and SMTP_PASS and SMTP_HOST:
        send_email(
            EMAIL_FROM,
            "New Contact Form Message",
            f"<b>From:</b> {name}<br><b>Email:</b> {email}<br><br>{msg}"
        )

    print("CONTACT MESSAGE:", name, email, msg)

    return jsonify({"ok": True})

# -------------------------
# CONTACT PAGE ROUTE (Fix: must be ABOVE app.run)
# -------------------------
@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    msg = data.get("msg")

    # If SMTP configured → send mail
    if SMTP_USER and SMTP_PASS and SMTP_HOST:
        send_email(
            EMAIL_FROM,
            "New Contact Form Message",
            f"<b>From:</b> {name}<br><b>Email:</b> {email}<br><br>{msg}"
        )

    print("CONTACT MESSAGE:", name, email, msg)
    return jsonify({"ok": True})


# -------------------------
# MAIN ENTRY
# -------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
