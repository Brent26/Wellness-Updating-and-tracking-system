"""
app/models/user.py

User model with role-based access control.

Roles:
    wellness_manager  — full access + user onboarding
    assistant         — full access, no user management
    intern            — identical to assistant
    auditor           — read-only, periodics & employee status only, no biometrics
"""

import enum
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class UserRole(enum.Enum):
    wellness_manager = "wellness_manager"
    assistant        = "assistant"
    intern           = "intern"
    auditor          = "auditor"


# Human-readable labels for display in UI
ROLE_LABELS = {
    "wellness_manager": "Wellness Manager",
    "assistant":        "Assistant",
    "intern":           "Intern",
    "auditor":          "Auditor",
}

# Roles that can access biometrics
BIOMETRICS_ROLES = {"wellness_manager", "assistant", "intern"}

# Roles that can perform write operations (edit, upload, run tasks)
WRITE_ROLES = {"wellness_manager", "assistant", "intern"}


class User(db.Model):
    __tablename__ = "users"

    id                   = db.Column(db.Integer, primary_key=True)
    email                = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username             = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash        = db.Column(db.String(256), nullable=False)
    full_name            = db.Column(db.String(128), nullable=True)
    department           = db.Column(db.String(128), nullable=True)
    role                 = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.auditor)
    is_active            = db.Column(db.Boolean, default=True, nullable=False)
    must_change_password = db.Column(db.Boolean, default=True, nullable=False)
    created_by_id        = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at        = db.Column(db.DateTime, nullable=True)

    # Self-referencing relationship — who created this user
    created_by = db.relationship("User", remote_side=[id], backref="onboarded_users")

    # ── Password helpers ──────────────────────────────────────

    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    # ── Role helpers ──────────────────────────────────────────

    @property
    def role_value(self) -> str:
        return self.role.value

    @property
    def role_label(self) -> str:
        return ROLE_LABELS.get(self.role.value, self.role.value)

    @property
    def can_write(self) -> bool:
        return self.role.value in WRITE_ROLES

    @property
    def can_access_biometrics(self) -> bool:
        return self.role.value in BIOMETRICS_ROLES

    @property
    def can_manage_users(self) -> bool:
        return self.role.value == "wellness_manager"

    # ── Serialisation ─────────────────────────────────────────

    def to_dict(self):
        return {
            "id":           self.id,
            "email":        self.email,
            "username":     self.username,
            "full_name":    self.full_name,
            "department":   self.department,
            "role":         self.role.value,
            "role_label":   self.role_label,
            "is_active":    self.is_active,
            "created_at":   self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }

    def __repr__(self):
        return f"<User {self.username} [{self.role.value}]>"
