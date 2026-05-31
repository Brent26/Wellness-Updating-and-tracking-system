"""
seed_admin.py

Run ONCE after deploying the RBAC changes to:
  1. Create the `users` table (safe — db.create_all() never touches existing tables)
  2. Create the first wellness_manager account

Usage:
    python seed_admin.py

After running, log in with the credentials printed below and change your
password immediately when prompted.
"""

import os

from app import create_app
from app.extensions import db
from app.models.user import User, UserRole

app = create_app()

with app.app_context():
    db.create_all()

    if User.query.filter_by(role=UserRole.wellness_manager).first():
        print("=" * 50)
        print("  A wellness_manager account already exists.")
        print("  Skipping seed — no changes made.")
        print("=" * 50)
    else:
        admin = User(
            email=os.getenv("INITIAL_ADMIN_EMAIL", "admin@example.com"),
            username=os.getenv("INITIAL_ADMIN_USERNAME", "admin"),
            full_name=os.getenv("INITIAL_ADMIN_FULL_NAME", "System Administrator"),
            role=UserRole.wellness_manager,
            must_change_password=True,
            is_active=True,
        )
        temp_password = os.getenv("INITIAL_ADMIN_PASSWORD", "ChangeMeNow123!")
        admin.set_password(temp_password)
        db.session.add(admin)
        db.session.commit()

        print()
        print("=" * 50)
        print("  Wellness Manager account created.")
        print()
        print(f"  Username : {admin.username}")
        print(f"  Password : {temp_password}")
        print()
        print("  !! Log in and change this password immediately.")
        print("=" * 50)
        print()
