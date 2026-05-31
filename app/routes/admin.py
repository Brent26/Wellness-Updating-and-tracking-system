"""
app/routes/admin.py

User management blueprint — accessible only by wellness_manager.
Handles listing, onboarding, and deactivating platform users.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session
from app.extensions import db
from app.routes.auth import login_required, role_required, generate_temp_password

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/users")
@login_required
@role_required("wellness_manager")
def users():
    from app.models.user import User
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/admin/users/new", methods=["GET", "POST"])
@login_required
@role_required("wellness_manager")
def create_user():
    from app.models.user import User, UserRole
    error = None

    if request.method == "POST":
        full_name  = request.form.get("full_name",  "").strip()
        email      = request.form.get("email",      "").strip().lower()
        username   = request.form.get("username",   "").strip().lower()
        department = request.form.get("department", "").strip()
        role_str   = request.form.get("role", "auditor")

        # Validate role is one of the allowed values
        allowed_roles = [r.value for r in UserRole]
        if role_str not in allowed_roles:
            error = "Invalid role selected."
        elif not full_name:
            error = "Full name is required."
        elif not email or "@" not in email:
            error = "A valid email address is required."
        elif not username:
            error = "Username is required."
        elif User.query.filter_by(email=email).first():
            error = "A user with that email already exists."
        elif User.query.filter_by(username=username).first():
            error = "That username is already taken."
        else:
            temp_password = generate_temp_password()
            new_user = User(
                email=email,
                username=username,
                full_name=full_name,
                department=department or None,
                role=UserRole[role_str],
                must_change_password=True,
                is_active=True,
                created_by_id=session.get("user_id"),
            )
            new_user.set_password(temp_password)
            db.session.add(new_user)
            db.session.commit()
            return render_template(
                "admin/user_created.html",
                new_user=new_user,
                temp_password=temp_password,
            )

    return render_template("admin/user_form.html", error=error)


@admin_bp.route("/admin/users/<int:user_id>/toggle", methods=["POST"])
@login_required
@role_required("wellness_manager")
def toggle_user(user_id):
    from app.models.user import User
    user = User.query.get_or_404(user_id)

    # Prevent deactivating yourself
    if user.id == session.get("user_id"):
        return redirect(url_for("admin.users"))

    user.is_active = not user.is_active
    db.session.commit()
    return redirect(url_for("admin.users"))


@admin_bp.route("/admin/users/<int:user_id>/reset-password", methods=["POST"])
@login_required
@role_required("wellness_manager")
def reset_password(user_id):
    from app.models.user import User
    user = User.query.get_or_404(user_id)
    temp_password = generate_temp_password()
    user.set_password(temp_password)
    user.must_change_password = True
    db.session.commit()
    return render_template(
        "admin/user_created.html",
        new_user=user,
        temp_password=temp_password,
        is_reset=True,
    )
