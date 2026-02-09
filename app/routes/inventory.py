"""Inventory listing page."""

from flask import Blueprint, render_template

from app.extensions import db
from app.models.topsoil import Topsoil

inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.route("/inventory")
def inventory():
    """Display all available topsoil products."""
    products = db.session.execute(
        db.select(Topsoil).order_by(Topsoil.name)
    ).scalars().all()
    return render_template("inventory.html", products=products)
