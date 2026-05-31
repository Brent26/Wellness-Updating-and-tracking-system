"""
app/routes/auth.py

Authentication routes and access-control decorators.

Decorators
----------
login_required          — user must be signed in
write_required          — blocks auditor from any state-changing operation
biometrics_required     — blocks auditor from biometrics page & API
role_required(*roles)   — restrict to specific role(s)
"""

from app import limiter
import secrets
import string
from datetime import datetime
from functools import wraps

from flask import (
    Blueprint, abort, jsonify, redirect, render_template,
    request, session, url_for
)
from app.extensions import db

auth_bp = Blueprint("auth", __name__)


# ── Helpers ────────────────────────────────────────────────────────────────────

def get_current_user():
    """Load the logged-in User from the DB. Returns None if not logged in."""
    from app.models.user import User
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)


def generate_temp_password(length: int = 12) -> str:
    """Return a cryptographically secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$"
    return "".join(secrets.choice(alphabet) for _ in range(length))


# ── Decorators ─────────────────────────────────────────────────────────────────

def login_required(f):
    """Redirect to login if the user is not authenticated."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrapper


def write_required(f):
    """
    Block auditors from write operations.
    Returns JSON 403 for API routes, HTML 403 for page routes.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        role = session.get("user_role", "")
        if role == "auditor":
            # API routes expect JSON
            if request.path.startswith("/api/"):
                return jsonify({"error": "Insufficient permissions — read-only access."}), 403
            abort(403)
        return f(*args, **kwargs)
    return wrapper


def biometrics_required(f):
    """
    Block auditors from the biometrics page and all biometric API endpoints.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        role = session.get("user_role", "")
        if role == "auditor":
            if request.path.startswith("/api/"):
                return jsonify({"error": "Access to biometric data is restricted."}), 403
            # Page route — redirect home with a message stored in session
            session["access_error"] = "You do not have permission to access the Biometrics page."
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return wrapper


def role_required(*roles):
    """
    Restrict a route to one or more named roles.
    Usage: @role_required("wellness_manager")
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            role = session.get("user_role", "")
            if role not in roles:
                if request.path.startswith("/api/"):
                    return jsonify({"error": "Insufficient permissions."}), 403
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ── Routes ─────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    # Already logged in
    if session.get("user_id"):
        return redirect(url_for("dashboard.index"))

    error = None
    if request.method == "POST":
        from app.models.user import User
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username, is_active=True).first()

        if user and user.check_password(password):
            session["user_id"]   = user.id
            session["user_role"] = user.role.value
            user.last_login_at   = datetime.utcnow()
            db.session.commit()

            # Force password change on first login
            if user.must_change_password:
                return redirect(url_for("auth.change_password"))

            return redirect(url_for("dashboard.index"))

        error = "Invalid username or password."

    return render_template("login.html", error=error)


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    user  = get_current_user()
    error = None

    if request.method == "POST":
        new_pw  = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")

        if len(new_pw) < 8:
            error = "Password must be at least 8 characters."
        elif new_pw != confirm:
            error = "Passwords do not match."
        else:
            user.set_password(new_pw)
            user.must_change_password = False
            db.session.commit()
            return redirect(url_for("dashboard.index"))

    return render_template(
        "change_password.html",
        error=error,
        forced=user.must_change_password,
        full_name=user.full_name or user.username,
    )


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
