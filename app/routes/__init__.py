"""Blueprint registration for the Topsoil Marketplace."""


def register_blueprints(app):
    from app.routes.main import main_bp
    from app.routes.inventory import inventory_bp
    from app.routes.checkout import checkout_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(admin_bp)
