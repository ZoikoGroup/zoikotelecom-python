"""
Serializers for the bqorders endpoint.

The Next.js client posts the `data` field returned by processOrderStripe(),
which is a single flat object combining customer-entered data and the BT
response. We accept it verbatim and unpack it into BTOrder columns.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from django.utils.dateparse import parse_datetime
from rest_framework import serializers

from .models import BTOrder, BTOrderEvent, BTOrderState, LocalStatus

def _dec(value: Any, default: str = "0") -> Decimal:
    """Coerce loose JSON numbers/strings to Decimal safely."""
    if value is None or value == "":
        return Decimal(default)
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal(default)


def _str(value: Any) -> str:
    return "" if value is None else str(value)


# ─── Nested input shapes (for documentation / light validation) ──────────────

class _BillingAddressIn(serializers.Serializer):
    firstName    = serializers.CharField(max_length=120)
    lastName     = serializers.CharField(max_length=120, required=False, allow_blank=True)
    email        = serializers.EmailField()
    phone        = serializers.CharField(max_length=40, required=False, allow_blank=True)
    companyName  = serializers.CharField(max_length=200, required=False, allow_blank=True)
    street       = serializers.CharField(max_length=255, required=False, allow_blank=True)
    houseNumber  = serializers.CharField(max_length=40,  required=False, allow_blank=True)
    city         = serializers.CharField(max_length=120, required=False, allow_blank=True)
    region       = serializers.CharField(max_length=120, required=False, allow_blank=True)
    state        = serializers.CharField(max_length=120, required=False, allow_blank=True)
    zip          = serializers.CharField(max_length=20,  required=False, allow_blank=True)


class _ServiceAddressIn(serializers.Serializer):
    id        = serializers.CharField(max_length=64)
    postcode  = serializers.CharField(max_length=20,  required=False, allow_blank=True)
    streetNr  = serializers.CharField(max_length=40,  required=False, allow_blank=True)
    streetName= serializers.CharField(max_length=255, required=False, allow_blank=True)
    city      = serializers.CharField(max_length=120, required=False, allow_blank=True)
    districtCode = serializers.CharField(max_length=8, required=False, allow_blank=True)
    qualifier = serializers.CharField(max_length=32,  required=False, allow_blank=True)


class _TotalsIn(serializers.Serializer):
    subtotal = serializers.FloatField()
    discount = serializers.FloatField()
    total    = serializers.FloatField()


# ─── Main input serializer ───────────────────────────────────────────────────

class BTOrderCreateSerializer(serializers.Serializer):
    """
    Validates and persists the payload from Next.js processOrderStripe().

    Required (anything else is optional and stored in *_raw blobs):
      - externalId
      - billingAddress.email + firstName
      - cart (non-empty list)
    """

    # BT-side
    externalId       = serializers.CharField(max_length=128)
    btOrderId        = serializers.CharField(max_length=128, required=False, allow_blank=True)
    btStatus         = serializers.CharField(max_length=16,  required=False, allow_blank=True)
    btData           = serializers.JSONField(required=False, default=dict)
    appointmentId    = serializers.CharField(max_length=64,  required=False, allow_blank=True)
    appointmentStart = serializers.CharField(required=False, allow_blank=True)
    appointmentEnd   = serializers.CharField(required=False, allow_blank=True)


    # Customer-side
    billingAddress   = _BillingAddressIn()
    shippingAddress  = _BillingAddressIn(required=False)
    serviceAddress   = _ServiceAddressIn(required=False)
    cart             = serializers.ListField(child=serializers.JSONField(), allow_empty=False)
    totals           = _TotalsIn(required=False)
    coupon           = serializers.JSONField(required=False, allow_null=True, default=None)
    paymentMethod    = serializers.CharField(max_length=16, required=False, default="stripe")
    agreedToTerms    = serializers.BooleanField(required=False, default=False)
    createdAt        = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data: dict) -> BTOrder:
        billing  = validated_data["billingAddress"]
        shipping = validated_data.get("shippingAddress") or billing
        service  = validated_data.get("serviceAddress") or {}
        totals   = validated_data.get("totals") or {}
        coupon   = validated_data.get("coupon") or {}
        cart     = validated_data["cart"]

        # Pull product summary out of the first cart item (Zoiko: one plan per order).
        first_item = cart[0] if cart else {}
        product = first_item.get("product") or {}
        zoiko   = first_item.get("zoikoPlan") or {}

        # Normalise local status from the BT route's status field.
        bt_status_raw = (validated_data.get("btStatus") or "").lower()
        local_status = {
            "created": LocalStatus.CREATED,
            "pending": LocalStatus.PENDING,
        }.get(bt_status_raw, LocalStatus.UNKNOWN)

        # Initial bt_state — BT acknowledges every successful order with "acknowledged"
        # before its webhook starts pushing updates. Empty if local_status is FAILED.
        initial_bt_state = (
            BTOrderState.ACKNOWLEDGED.value
            if local_status in (LocalStatus.CREATED, LocalStatus.PENDING)
            else ""
        )

        # Pass through anything the caller didn't model, for audit.
        raw_envelope = self.initial_data if isinstance(self.initial_data, dict) else {}

        order = BTOrder.objects.create(
            external_id  = validated_data["externalId"],
            bt_order_id  = validated_data.get("btOrderId") or "",
            local_status = local_status,
            bt_state     = initial_bt_state,

            # Billing contact
            first_name   = _str(billing.get("firstName")),
            last_name    = _str(billing.get("lastName")),
            email        = _str(billing.get("email")),
            phone        = _str(billing.get("phone")),
            company_name = _str(billing.get("companyName")),
            billing_street       = _str(billing.get("street")),
            billing_house_number = _str(billing.get("houseNumber")),
            billing_city         = _str(billing.get("city")),
            billing_region       = _str(billing.get("region")),
            billing_state        = _str(billing.get("state")),
            billing_zip          = _str(billing.get("zip")),

            # Service address
            service_address_id   = _str(service.get("id")),
            service_postcode     = _str(service.get("postcode")),
            service_city         = _str(service.get("city")),
            service_street_name  = _str(service.get("streetName")),
            service_street_nr    = _str(service.get("streetNr")),
            service_district     = _str(service.get("districtCode")),
            service_qualifier    = _str(service.get("qualifier")),

            # Product summary
            product_name        = _str(first_item.get("name") or zoiko.get("name")),
            product_offering_id = _str((product.get("offering") or {}).get("id") or product.get("id")),
            contract_term       = _str(zoiko.get("contractType") or first_item.get("validity")),
            download_speed      = _str(product.get("download") or first_item.get("speed")),
            upload_speed        = _str(product.get("upload")),

            # Appointment
            appointment_id    = _str(validated_data.get("appointmentId")),
            appointment_start = parse_datetime(validated_data.get("appointmentStart") or "") or None,
            appointment_end   = parse_datetime(validated_data.get("appointmentEnd")   or "") or None,

            # Money
            subtotal = _dec(totals.get("subtotal")),
            discount = _dec(totals.get("discount")),
            total    = _dec(totals.get("total")),
            coupon_code     = _str((coupon or {}).get("code")),
            coupon_type     = _str((coupon or {}).get("type")),
            coupon_discount = _str((coupon or {}).get("discount")),

            payment_method   = _str(validated_data.get("paymentMethod")) or "stripe",
            agreed_to_terms  = bool(validated_data.get("agreedToTerms")),
            client_created_at = parse_datetime(validated_data.get("createdAt") or "") or None,

            # Raw blobs
            cart_raw             = cart,
            service_address_raw  = service,
            billing_address_raw  = billing,
            shipping_address_raw = shipping,
            totals_raw           = totals,
            coupon_raw           = coupon,
            bt_response_raw      = validated_data.get("btData") or {},
            request_payload_raw  = raw_envelope,
        )

        # Initial event — captures the exact creation moment.
        BTOrderEvent.objects.create(
            order        = order,
            external_id  = order.external_id,
            source       = BTOrderEvent.Source.CHECKOUT,
            event_type   = "OrderCreated",
            state        = order.bt_state,
            payload_raw  = validated_data.get("btData") or {},
        )

        return order


# ─── Output serializer (GET / response after POST) ───────────────────────────

class BTOrderReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = BTOrder
        fields = [
            "id", "external_id", "bt_order_id",
            "local_status", "bt_state", "error_message",
            "first_name", "last_name", "email", "phone",
            "service_address_id", "service_postcode",
            "product_name", "product_offering_id", "contract_term",
            "appointment_id", "appointment_start", "appointment_end",
            "subtotal", "discount", "total", "currency",
            "payment_method", "agreed_to_terms",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


# ─── Webhook serializer (BT API 8) ───────────────────────────────────────────

class BTWebhookSerializer(serializers.Serializer):
    """
    Validates inbound BT state-change notifications (API 8).

    Shape (from BT docs):
      {
        "event": {
          "productOrder": {
            "externalId": "WC-123",
            "id":         "ORD-...",
            "errorMessage": [...],
            "productOrderItem": [...],
            ...
          }
        },
        "eventType": "ProductOrderStateChangeEvent",
        "eventTime": "...",
        "eventId":   "..."
      }
    """
    event     = serializers.JSONField()
    eventType = serializers.CharField(required=False, allow_blank=True)
    eventTime = serializers.CharField(required=False, allow_blank=True)
    eventId   = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        po = (attrs.get("event") or {}).get("productOrder") or {}
        if not po.get("externalId") and not po.get("id"):
            raise serializers.ValidationError(
                "event.productOrder must contain externalId or id."
            )
        return attrs
