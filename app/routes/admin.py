"""Admin dashboard: order management, inventory updates, and banner control."""

import hmac
from functools import wraps

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.extensions import db
from app.models.order import Order
from app.models.site_settings import SiteSettings
from app.models.topsoil import Topsoil
from app.models.work_order import WorkOrder

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ---------------------------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------------------------

def admin_required(view_func):
    """Decorator that redirects unauthenticated visitors to the admin login."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            flash("Please log in to access the admin area.", "error")
            return redirect(url_for("admin.login"))
        return view_func(*args, **kwargs)

    return wrapped


# ---------------------------------------------------------------------------
# Login / Logout
# ---------------------------------------------------------------------------

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    """Render and process the admin login form."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        expected_username = current_app.config["ADMIN_USERNAME"]
        expected_password = current_app.config["ADMIN_PASSWORD"]

        if hmac.compare_digest(username, expected_username) and hmac.compare_digest(password, expected_password):
            session["admin"] = True
            flash("Logged in successfully.", "success")
            return redirect(url_for("admin.dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("admin/login.html")


@admin_bp.route("/logout", methods=["POST"])
def logout():
    """Clear the admin session and redirect to the public home page."""
    session.pop("admin", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))


# ---------------------------------------------------------------------------
# Dashboard -- Work-order overview
# ---------------------------------------------------------------------------

@admin_bp.route("/")
@admin_required
def dashboard():
    """List all work orders with associated order details, newest first."""
    status_filter = request.args.get("status", "all")

    query = db.select(WorkOrder).join(WorkOrder.order)

    if status_filter == "pending":
        query = query.where(Order.status == "Pending")
    elif status_filter == "completed":
        query = query.where(Order.status == "Completed")

    work_orders = (
        db.session.execute(query.order_by(WorkOrder.date_assigned.desc()))
        .scalars()
        .all()
    )
    return render_template(
        "admin/dashboard.html",
        work_orders=work_orders,
        status_filter=status_filter,
        active_page="dashboard",
    )


# ---------------------------------------------------------------------------
# Order management
# ---------------------------------------------------------------------------

@admin_bp.route("/orders/<int:order_id>/complete", methods=["POST"])
@admin_required
def complete_order(order_id):
    """Mark an order as completed."""
    order = db.session.get(Order, order_id)
    if order is None:
        flash("Order not found.", "error")
        return redirect(url_for("admin.dashboard"))

    order.status = "Completed"
    db.session.commit()
    flash(f"Order #{order.id} marked as completed.", "success")
    return redirect(url_for("admin.dashboard"))


# ---------------------------------------------------------------------------
# Inventory management
# ---------------------------------------------------------------------------

@admin_bp.route("/inventory")
@admin_required
def inventory():
    """List all topsoil products with editable price and stock fields."""
    products = (
        db.session.execute(db.select(Topsoil).order_by(Topsoil.name))
        .scalars()
        .all()
    )
    return render_template("admin/inventory.html", products=products, active_page="inventory")


@admin_bp.route("/inventory/<int:product_id>/update", methods=["POST"])
@admin_required
def update_inventory(product_id):
    """Update price and inventory count for a single product."""
    product = db.session.get(Topsoil, product_id)
    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("admin.inventory"))

    try:
        new_price = float(request.form.get("price_per_load", product.price_per_load))
        new_count = int(request.form.get("inventory_count", product.inventory_count))
    except (TypeError, ValueError):
        flash("Invalid input. Price must be a number and count must be a whole number.", "error")
        return redirect(url_for("admin.inventory"))

    if new_price < 0 or new_count < 0:
        flash("Price and inventory count must not be negative.", "error")
        return redirect(url_for("admin.inventory"))

    product.price_per_load = new_price
    product.inventory_count = new_count
    db.session.commit()

    flash(f"Updated {product.name} -- ${new_price:.2f}/load, {new_count} in stock.", "success")
    return redirect(url_for("admin.inventory"))


# ---------------------------------------------------------------------------
# Site settings (banner control)
# ---------------------------------------------------------------------------

@admin_bp.route("/settings", methods=["GET", "POST"])
@admin_required
def settings():
    """View and update the global site banner settings."""
    site_settings = db.session.get(SiteSettings, 1)

    # Auto-create the singleton row if it does not exist yet.
    if site_settings is None:
        site_settings = SiteSettings(id=1, banner_text="", banner_active=False)
        db.session.add(site_settings)
        db.session.commit()

    if request.method == "POST":
        site_settings.banner_text = request.form.get("banner_text", "").strip()
        # Checkbox only appears in form data when checked.
        if "banner_active" in request.form and not site_settings.banner_text:
            site_settings.banner_active = False
            db.session.commit()
            flash("Banner cannot be activated with empty text. Banner has been deactivated.", "error")
        else:
            site_settings.banner_active = "banner_active" in request.form
            db.session.commit()
            flash("Site settings saved.", "success")
        return redirect(url_for("admin.settings"))

    return render_template("admin/settings.html", settings=site_settings, active_page="settings")
