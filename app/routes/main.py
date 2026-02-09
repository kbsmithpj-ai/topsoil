"""Public pages: home and about."""

from flask import Blueprint, render_template

from app.models.site_settings import SiteSettings

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    """Landing page."""
    settings = SiteSettings.query.first()
    return render_template("home.html", settings=settings)


@main_bp.route("/about")
def about():
    """About page."""
    return render_template("about.html")
