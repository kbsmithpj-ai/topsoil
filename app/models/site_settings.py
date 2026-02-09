from app.extensions import db


class SiteSettings(db.Model):
    """Global site configuration such as promotional banners.

    This table is designed to hold a single row (id=1) that is read on
    every public page load and edited through the admin settings panel.
    """

    __tablename__ = "site_settings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    banner_text = db.Column(db.Text, nullable=True)
    banner_active = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        active_label = "ON" if self.banner_active else "OFF"
        return f"<SiteSettings banner={active_label}>"
