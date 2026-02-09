from app.extensions import db


class Topsoil(db.Model):
    """A topsoil product available for purchase."""

    __tablename__ = "topsoil"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    soil_type = db.Column(db.String(20), nullable=False)  # "Screened" or "Raw"
    price_per_load = db.Column(db.Float, nullable=False)
    inventory_count = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))

    orders = db.relationship("Order", back_populates="topsoil", lazy="select")

    def __repr__(self):
        return f"<Topsoil {self.id}: {self.name}>"
