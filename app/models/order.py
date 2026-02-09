from datetime import datetime, timezone

from app.extensions import db


class Order(db.Model):
    """A customer order for a topsoil product."""

    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topsoil_id = db.Column(
        db.Integer, db.ForeignKey("topsoil.id"), nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    topsoil = db.relationship("Topsoil", back_populates="orders")
    work_order = db.relationship(
        "WorkOrder", back_populates="order", uselist=False
    )

    def __repr__(self):
        return f"<Order {self.id}: {self.customer_name} - {self.status}>"
