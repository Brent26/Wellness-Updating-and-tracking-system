from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_config.settings import Config
from app.extensions import db, migrate

csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=[])


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)

    with app.app_context():
        from app.models import (
            JobRun,
            HeadcountRecord,
            MedicRecord,
            ConflictLog,
            PeriodicRecord,
            RecordChangeLog,
            User,           # registers the users table
        )
        db.create_all()

    app.secret_key = app.config["SECRET_KEY"]

    # ── Context processor — injects current_user & user_role into every template
    @app.context_processor
    def inject_current_user():
        from app.routes.auth import get_current_user
        user = get_current_user()
        return {
            "current_user": user,
            "user_role":    user.role.value if user else None,
            "app_name": app.config["APP_NAME"],
            "app_short_name": app.config["APP_SHORT_NAME"],
            "company_name": app.config["COMPANY_NAME"],
            "app_brand": app.config["APP_BRAND"],
        }

    # ── Blueprints ────────────────────────────────────────────────────────────
    from app.routes.dashboard import dashboard_bp
    from app.routes.api       import api_bp
    from app.routes.stream    import stream_bp
    from app.routes.auth      import auth_bp
    from app.routes.admin     import admin_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp,    url_prefix="/api")
    app.register_blueprint(stream_bp, url_prefix="/stream")
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    return app
