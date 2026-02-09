"""Checkout flow: order form, submission, and confirmation."""

import re

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from app.extensions import db
from app.models.order import Order
from app.models.topsoil import Topsoil
from app.services import order_service

checkout_bp = Blueprint("checkout", __name__)

# Matches digits, dashes, parentheses, spaces, and optional leading +.
# Requires at least 7 digit-like characters total.
_PHONE_PATTERN = re.compile(r"^[\d\s\-\(\)\+\.]+$")
_PHONE_MIN_DIGITS = 7


def _validate_checkout_form(form, topsoil):
    """Validate the checkout form fields.

    Returns a dict of field-name -> error-message strings.  An empty
    dict means the form is valid.
    """
    errors = {}

    customer_name = form.get("customer_name", "").strip()
    customer_email = form.get("customer_email", "").strip()
    customer_phone = form.get("customer_phone", "").strip()
    delivery_address = form.get("delivery_address", "").strip()
    quantity_raw = form.get("quantity", "").strip()

    # --- Name --------------------------------------------------------------
    if not customer_name:
        errors["customer_name"] = "Full name is required."

    # --- Email -------------------------------------------------------------
    if not customer_email:
        errors["customer_email"] = "Email address is required."
    elif "@" not in customer_email or "." not in customer_email:
        errors["customer_email"] = "Please enter a valid email address."

    # --- Phone -------------------------------------------------------------
    if not customer_phone:
        errors["customer_phone"] = "Phone number is required."
    elif not _PHONE_PATTERN.match(customer_phone):
        errors["customer_phone"] = (
            "Phone number may only contain digits, dashes, parentheses, "
            "spaces, and a leading +."
        )
    elif sum(c.isdigit() for c in customer_phone) < _PHONE_MIN_DIGITS:
        errors["customer_phone"] = "Phone number must contain at least 7 digits."

    # --- Delivery address --------------------------------------------------
    if not delivery_address:
        errors["delivery_address"] = "Delivery address is required."

    # --- Quantity ----------------------------------------------------------
    if not quantity_raw:
        errors["quantity"] = "Number of tandem loads is required."
    else:
        try:
            quantity = int(quantity_raw)
        except (ValueError, TypeError):
            errors["quantity"] = "Quantity must be a whole number."
            quantity = None

        if quantity is not None:
            if quantity < 1:
                errors["quantity"] = "You must order at least 1 tandem load."
            elif quantity > topsoil.inventory_count:
                errors["quantity"] = (
                    f"Only {topsoil.inventory_count} load(s) currently available."
                )

    return errors


@checkout_bp.route("/checkout/<int:topsoil_id>", methods=["GET"])
def checkout(topsoil_id):
    """Display the checkout form for a specific product."""
    topsoil = db.session.get(Topsoil, topsoil_id)
    if topsoil is None:
        abort(404)
    return render_template("checkout.html", product=topsoil)


@checkout_bp.route("/checkout/<int:topsoil_id>", methods=["POST"])
def checkout_submit(topsoil_id):
    """Process the checkout form submission."""
    topsoil = db.session.get(Topsoil, topsoil_id)
    if topsoil is None:
        abort(404)

    errors = _validate_checkout_form(request.form, topsoil)
    if errors:
        return render_template("checkout.html", product=topsoil, errors=errors), 422

    try:
        order = order_service.place_order(
            topsoil_id=topsoil_id,
            quantity=int(request.form["quantity"]),
            customer_name=request.form["customer_name"].strip(),
            customer_email=request.form["customer_email"].strip(),
            customer_phone=request.form["customer_phone"].strip(),
            delivery_address=request.form["delivery_address"].strip(),
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return render_template("checkout.html", product=topsoil), 422
    except Exception:
        flash(
            "An unexpected error occurred while placing your order. "
            "Please try again.",
            "error",
        )
        return render_template("checkout.html", product=topsoil), 500

    session.setdefault('confirmed_orders', []).append(order.id)
    flash("Your order has been placed successfully!", "success")
    return redirect(url_for("checkout.order_confirmation", order_id=order.id))


@checkout_bp.route("/order-confirmation/<int:order_id>")
def order_confirmation(order_id):
    """Display the order confirmation page."""
    if order_id not in session.get('confirmed_orders', []):
        abort(403)

    order = db.session.get(Order, order_id)
    if order is None:
        abort(404)

    # Eagerly load the related topsoil product so the template has access.
    topsoil = order.topsoil

    return render_template("order_confirm.html", order=order, product=topsoil)
