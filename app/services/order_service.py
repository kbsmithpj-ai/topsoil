"""Order placement and fulfillment logic."""

import logging
from datetime import datetime, timezone

from app.extensions import db
from app.models.order import Order
from app.models.topsoil import Topsoil
from app.models.work_order import WorkOrder
from app.services.mail_service import send_work_order_email

logger = logging.getLogger(__name__)


def place_order(
    topsoil_id,
    quantity,
    customer_name,
    customer_email,
    customer_phone,
    delivery_address,
):
    """Create an Order and its companion WorkOrder in a single transaction.

    Decrements the product's inventory count and attempts to send an email
    notification to the site manager.  The email step is best-effort -- a
    delivery failure will not roll back the order.

    Returns the newly created :class:`Order` instance.

    Raises:
        ValueError: If the requested quantity exceeds available inventory.
        Exception:  Re-raises any database error after rolling back.
    """
    topsoil = db.session.get(Topsoil, topsoil_id)
    if topsoil is None:
        raise ValueError(f"Topsoil product with id {topsoil_id} not found.")

    if quantity > topsoil.inventory_count:
        raise ValueError(
            f"Requested {quantity} load(s) but only "
            f"{topsoil.inventory_count} available."
        )

    total_price = quantity * topsoil.price_per_load

    order = Order(
        topsoil_id=topsoil_id,
        quantity=quantity,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        delivery_address=delivery_address,
        total_price=total_price,
        status="Pending",
    )

    work_order = WorkOrder(
        order=order,
        date_assigned=datetime.now(timezone.utc),
        notification_sent=False,
    )

    topsoil.inventory_count -= quantity

    try:
        db.session.add(order)
        db.session.add(work_order)
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("Database error while placing Order.")
        raise

    # Email notification is best-effort; do not roll back the order if
    # the mail server is unavailable.
    email_sent = send_work_order_email(work_order, order, topsoil)
    if email_sent:
        try:
            work_order.notification_sent = True
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception(
                "Failed to update notification_sent flag for "
                "WorkOrder #%s.",
                work_order.id,
            )

    return order
