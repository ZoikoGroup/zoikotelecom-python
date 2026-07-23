"""
Order notification email.

EE mobile and landline orders are *not* placed with BT Wholesale, so there is
no downstream system to action them. Instead we email the fulfilment inbox
(orders@zoikotelecom.com by default) with the order details.

`send_order_notification` never raises — it returns (ok, error_message) so the
caller can record the outcome on the order (mail_status / mail_error) without
the email ever blocking the order from being saved.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils import timezone

logger = logging.getLogger("apps.orders")

# Override in settings if needed.
DEFAULT_ORDERS_INBOX = "orders@zoikotelecom.com"



def _orders_inbox() -> str:
    return getattr(settings, "ORDERS_NOTIFICATION_EMAIL", "") or DEFAULT_ORDERS_INBOX


# Symbol lookup for the customer-facing confirmation. The stored currency is
# GBP by default (see BTOrder.currency); we fall back to "£" for anything we
# don't recognise so a receipt never shows a bare code.
_CURRENCY_SYMBOLS = {
    "GBP": "£", "USD": "$", "EUR": "€", "AUD": "$", "CAD": "$", "NZD": "$",
}


def _currency_symbol(order) -> str:
    code = (getattr(order, "currency", "") or "GBP").upper()
    return _CURRENCY_SYMBOLS.get(code, "£")


def _line(label: str, value) -> str:
    value = "" if value is None else str(value)
    return f"{label}: {value}"


def build_order_email_body(order) -> tuple[str, str]:
    """Return (plain_text, html) bodies for the notification email."""
    type_label = order.get_order_type_display()
    full_name = " ".join(p for p in [order.first_name, order.last_name] if p).strip()

    # Items summary from the raw cart (full data, all types).
    item_lines: list[str] = []
    for it in order.cart_raw or []:
        if not isinstance(it, dict):
            continue
        name = it.get("name") or it.get("planName") or it.get("title") or "Item"
        price = it.get("price") or it.get("finalPrice") or it.get("pricePerUnit") or ""
        bits = [str(name)]
        if it.get("planDuration") or it.get("validity"):
            bits.append(f"· {it.get('planDuration') or it.get('validity')}")
        if it.get("dataAllowance"):
            bits.append(f"· {it.get('dataAllowance')}")
        if it.get("simType"):
            bits.append(f"· {it.get('simType')}")
        if it.get("speed"):
            bits.append(f"· {it.get('speed')} Mbps")
        if price != "":
            bits.append(f"— £{price}")
        item_lines.append("  " + " ".join(bits))
    items_block = "\n".join(item_lines) or "  (no items)"

    text = "\n".join([
        f"New {type_label} order received",
        "=" * 40,
        _line("Order ref", order.external_id),
        _line("Type", type_label),
        _line("Placed", timezone.localtime(order.created_at).strftime("%Y-%m-%d %H:%M")
              if order.created_at else ""),
        "",
        "Customer",
        "-" * 20,
        _line("Name", full_name),
        _line("Email", order.email),
        _line("Phone", order.phone),
        _line("Company", order.company_name),
        "",
        "Billing address",
        "-" * 20,
        _line("Street", f"{order.billing_house_number} {order.billing_street}".strip()),
        _line("City", order.billing_city),
        _line("State/Region", f"{order.billing_state} {order.billing_region}".strip()),
        _line("ZIP", order.billing_zip),
        "",
        "Items",
        "-" * 20,
        items_block,
        "",
        "Totals",
        "-" * 20,
        _line("Subtotal", f"£{order.subtotal}"),
        _line("Discount", f"£{order.discount}"),
        _line("Total", f"£{order.total}"),
        _line("Payment", order.get_payment_method_display()),
    ])

    rows = "".join(
        f"<tr><td style='padding:2px 12px 2px 0;color:#555'>{lbl}</td>"
        f"<td style='padding:2px 0'><strong>{val}</strong></td></tr>"
        for lbl, val in [
            ("Order ref", order.external_id),
            ("Type", type_label),
            ("Name", full_name),
            ("Email", order.email),
            ("Phone", order.phone),
            ("Total", f"£{order.total}"),
        ]
    )
    items_html = "".join(f"<li>{ln.strip()}</li>" for ln in item_lines) or "<li>(no items)</li>"
    html = (
        f"<div style='font-family:Arial,sans-serif;font-size:14px;color:#222'>"
        f"<h2 style='color:#c61b7f;margin:0 0 12px'>New {type_label} order</h2>"
        f"<table style='border-collapse:collapse'>{rows}</table>"
        f"<h3 style='margin:16px 0 6px'>Items</h3>"
        f"<ul style='margin:0;padding-left:18px'>{items_html}</ul>"
        f"</div>"
    )
    return text, html


def send_order_notification(order) -> tuple[bool, str]:
    """
    Email the fulfilment inbox about an EE mobile / landline order.

    Returns (ok, error). Never raises.
    """
    try:
        type_label = order.get_order_type_display()
        subject = f"New {type_label} order — {order.external_id}"
        text_body, html_body = build_order_email_body(order)

        # Hard timeout so a misconfigured / slow SMTP host can never hang the
        # order-save request (which would let gunicorn kill the worker and
        # return a 502 to the checkout). Falls back to 15s if unset.
        timeout = getattr(settings, "ORDERS_EMAIL_TIMEOUT", None) \
            or getattr(settings, "EMAIL_TIMEOUT", None) or 15
        connection = get_connection(timeout=timeout)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            to=[_orders_inbox()],
            reply_to=[order.email] if order.email else None,
            connection=connection,
        )
        msg.attach_alternative(html_body, "text/html")
        sent = msg.send(fail_silently=False)

        if sent:
            logger.info("[orders] Notification email sent for %s", order.external_id)
            return True, ""

        logger.warning("[orders] Notification email returned 0 for %s", order.external_id)
        return False, "Email backend reported 0 messages sent."
    except Exception as exc:  # noqa: BLE001 — must never break the order save
        logger.exception("[orders] Notification email failed for %s: %s", order.external_id, exc)
        return False, str(exc)


# ─── Customer confirmation email (ALL order types) ────────────────────────────
#
# The receipt sent to the *customer* after checkout. The success screen already
# promises "a confirmation email has been sent to <you>", so this must fire for
# every order type. Like send_order_notification it never raises — it returns
# (ok, error) so the caller can record the outcome without ever blocking the
# order save.


def build_order_confirmation_body(order) -> tuple[str, str]:
    """Return (plain_text, html) bodies for the customer confirmation receipt."""
    sym = _currency_symbol(order)
    type_label = order.get_order_type_display()
    full_name = " ".join(p for p in [order.first_name, order.last_name] if p).strip()
    greeting_name = order.first_name or full_name or "there"

    # Line items from the raw cart (same shape the notification uses).
    item_lines: list[str] = []
    item_rows_html: list[str] = []
    for it in order.cart_raw or []:
        if not isinstance(it, dict):
            continue
        name = it.get("name") or it.get("planName") or it.get("title") or "Item"
        price = it.get("price") or it.get("finalPrice") or it.get("pricePerUnit") or ""
        bits = [str(name)]
        if it.get("planDuration") or it.get("validity"):
            bits.append(f"· {it.get('planDuration') or it.get('validity')}")
        if it.get("dataAllowance"):
            bits.append(f"· {it.get('dataAllowance')}")
        if it.get("simType"):
            bits.append(f"· {it.get('simType')}")
        if it.get("speed"):
            bits.append(f"· {it.get('speed')} Mbps")
        price_txt = f"{sym}{price}" if price != "" else ""
        if price_txt:
            bits.append(f"— {price_txt}")
        item_lines.append("  " + " ".join(bits))
        item_rows_html.append(
            f"<tr><td style='padding:6px 0;border-bottom:1px solid #f0f0f0'>{name}</td>"
            f"<td style='padding:6px 0;border-bottom:1px solid #f0f0f0;text-align:right'>{price_txt or '—'}</td></tr>"
        )
    items_block = "\n".join(item_lines) or "  (no items)"
    items_html = "".join(item_rows_html) or (
        "<tr><td style='padding:6px 0'>(no items)</td><td></td></tr>"
    )

    # What-happens-next differs by product family.
    if order.order_type in ("accessories", "phone_equipment"):
        next_step = "We're preparing your order for dispatch and will email you tracking details once it ships."
    elif order.order_type == "broadband":
        next_step = "We're processing your broadband order. We'll be in touch about your installation and appointment."
    else:
        next_step = "Our team is now setting up your service and will be in touch shortly with the next steps."

    text = "\n".join([
        f"Hi {greeting_name},",
        "",
        f"Thanks for your order with Zoiko Telecom — we've received it successfully.",
        "",
        _line("Order reference", order.external_id),
        _line("Order type", type_label),
        "",
        next_step,
        "",
        "Order summary",
        "-" * 20,
        items_block,
        "",
        _line("Subtotal", f"{sym}{order.subtotal}"),
        _line("Discount", f"{sym}{order.discount}"),
        _line("Total paid", f"{sym}{order.total}"),
        "",
        "If anything looks wrong, just reply to this email and we'll help.",
        "",
        "— Zoiko Telecom",
    ])

    html = (
        f"<div style='font-family:Arial,sans-serif;font-size:14px;color:#222;max-width:560px'>"
        f"<h2 style='color:#c61b7f;margin:0 0 4px'>Thanks for your order!</h2>"
        f"<p style='margin:0 0 16px;color:#555'>Hi {greeting_name}, we've received your "
        f"{type_label} order successfully.</p>"
        f"<table style='border-collapse:collapse;margin-bottom:16px'>"
        f"<tr><td style='padding:2px 12px 2px 0;color:#555'>Order reference</td>"
        f"<td style='padding:2px 0'><strong>{order.external_id}</strong></td></tr>"
        f"</table>"
        f"<p style='margin:0 0 16px;color:#333'>{next_step}</p>"
        f"<h3 style='margin:16px 0 6px'>Order summary</h3>"
        f"<table style='border-collapse:collapse;width:100%'>{items_html}"
        f"<tr><td style='padding:8px 0;font-weight:600'>Total paid</td>"
        f"<td style='padding:8px 0;font-weight:700;text-align:right'>{sym}{order.total}</td></tr>"
        f"</table>"
        f"<p style='margin:18px 0 0;color:#777;font-size:13px'>If anything looks wrong, "
        f"just reply to this email and we'll help.</p>"
        f"<p style='margin:8px 0 0;color:#c61b7f;font-weight:600'>— Zoiko Telecom</p>"
        f"</div>"
    )
    return text, html


def send_order_confirmation(order) -> tuple[bool, str]:
    """
    Email the *customer* their order receipt. Fires for every order type.

    Returns (ok, error). Never raises.
    """
    try:
        if not order.email:
            return False, "Order has no customer email address."

        type_label = order.get_order_type_display()
        subject = f"Your Zoiko Telecom order — {order.external_id}"
        text_body, html_body = build_order_confirmation_body(order)

        # Same hard timeout rationale as the notification email: a slow SMTP
        # host must never hang the checkout request.
        timeout = getattr(settings, "ORDERS_EMAIL_TIMEOUT", None) \
            or getattr(settings, "EMAIL_TIMEOUT", None) or 15
        connection = get_connection(timeout=timeout)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            to=[order.email],
            reply_to=[_orders_inbox()],
            connection=connection,
        )
        msg.attach_alternative(html_body, "text/html")
        sent = msg.send(fail_silently=False)

        if sent:
            logger.info("[orders] Confirmation email sent to customer for %s", order.external_id)
            return True, ""

        logger.warning("[orders] Confirmation email returned 0 for %s", order.external_id)
        return False, "Email backend reported 0 messages sent."
    except Exception as exc:  # noqa: BLE001 — must never break the order save
        logger.exception("[orders] Confirmation email failed for %s: %s", order.external_id, exc)
        return False, str(exc)