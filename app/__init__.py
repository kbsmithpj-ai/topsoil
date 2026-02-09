from datetime import datetime, timezone

from flask import Flask

from config import Config
from app.extensions import db, mail, csrf


def create_app(config_class=Config):
    """Application factory for the Topsoil Marketplace."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app instance
    db.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # Make current_year available in all templates
    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.now(timezone.utc).year}

    # Register blueprints -- guarded so the app boots even when
    # route modules have not been created yet.
    try:
        from app.routes import register_blueprints
        register_blueprints(app)
    except (ImportError, AttributeError):
        pass

    # Ensure all tables exist
    with app.app_context():
        # Import models so SQLAlchemy is aware of them before create_all()
        from app import models  # noqa: F401
        db.create_all()

    return app
