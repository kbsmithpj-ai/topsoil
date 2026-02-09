from datetime import datetime, timezone

from app.extensions import db


class WorkOrder(db.Model):
    """A work order tied to a customer order, used for fulfillment tracking."""

    __tablename__ = "work_order"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("order.id"), unique=True, nullable=False
    )
    date_assigned = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    notification_sent = db.Column(db.Boolean, default=False)

    order = db.relationship("Order", back_populates="work_order")

    def __repr__(self):
        return f"<WorkOrder {self.id} for Order {self.order_id}>"
