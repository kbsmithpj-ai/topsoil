"""Email notification service for work order alerts."""

import logging

from flask import current_app
from flask_mail import Message

from app.extensions import mail

logger = logging.getLogger(__name__)


def send_work_order_email(work_order, order, topsoil):
    """Send a work order notification email to the site manager.

    Failures are handled gracefully -- the caller is never interrupted by
    an email error.  Returns True on success, False on failure.
    """
    recipient = current_app.config.get("MANAGER_EMAIL")
    if not recipient:
        logger.warning(
            "MANAGER_EMAIL is not configured; skipping work order "
            "notification for Order #%s.",
            order.id,
        )
        return False

    subject = f"New Work Order #{work_order.id} - {order.customer_name}"

    body = (
        f"A new work order has been created.\n"
        f"\n"
        f"Work Order:       #{work_order.id}\n"
        f"Order:            #{order.id}\n"
        f"\n"
        f"Customer Name:    {order.customer_name}\n"
        f"Phone:            {order.customer_phone}\n"
        f"Email:            {order.customer_email}\n"
        f"Delivery Address: {order.delivery_address}\n"
        f"\n"
        f"Product:          {topsoil.name}\n"
        f"Quantity:          {order.quantity} tandem load(s)\n"
        f"Total Price:      ${order.total_price:,.2f}\n"
    )

    try:
        msg = Message(subject=subject, recipients=[recipient], body=body)
        mail.send(msg)
        return True
    except Exception:
        logger.exception(
            "Failed to send work order email for Order #%s.", order.id
        )
        return False
