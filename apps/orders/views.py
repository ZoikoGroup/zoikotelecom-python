"""
API views for bqorders.

POST  /api/v1/bqorders/           Create an order (called by Next.js after BT succeeds).
GET   /api/v1/bqorders/<eid>/     Retrieve by external_id  (for the Thank You page).
POST  /api/v1/bqorders/webhook/   BT API 8 state-change notification landing zone.
"""

from __future__ import annotations

import logging
from typing import Any

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import BTOrder, BTOrderEvent, BTOrderState
from .serializers import (
    BTOrderCreateSerializer,
    BTOrderReadSerializer,
    BTWebhookSerializer,
)

logger = logging.getLogger("apps.orders")


# ─── Create + list ────────────────────────────────────────────────────────────


class BTOrderCreateView(views.APIView):
    """POST /api/v1/bqorders/ — create from Next.js processOrderStripe payload."""
    permission_classes = [AllowAny]   # Next.js calls server-to-server (no user token).
    authentication_classes: list = []

    def post(self, request, *args, **kwargs):
        serializer = BTOrderCreateSerializer(data=request.data)

        if not serializer.is_valid():
            logger.warning("[bqorders] Validation failed: %s", serializer.errors)
            return Response(
                {
                    "success": False,
                    "message": "Validation failed",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        external_id = serializer.validated_data["externalId"]

        try:
            with transaction.atomic():
                order = serializer.save()
        except IntegrityError:
            # Duplicate externalId — idempotent: return the existing record.
            existing = BTOrder.objects.filter(external_id=external_id).first()
            if existing:
                logger.info("[bqorders] Duplicate externalId %s — returning existing.", external_id)
                return Response(
                    {
                        "success": True,
                        "duplicate": True,
                        "message": "Order already saved.",
                        "data": BTOrderReadSerializer(existing).data,
                    },
                    status=status.HTTP_200_OK,
                )
            raise
        except Exception as exc:   # noqa: BLE001 - we want this in logs and a 500 back
            logger.exception("[bqorders] Failed to persist order %s: %s", external_id, exc)
            return Response(
                {"success": False, "message": "Internal error saving order."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        logger.info(
            "[bqorders] ✅ Saved order id=%s external_id=%s bt_order_id=%s status=%s",
            order.pk, order.external_id, order.bt_order_id, order.local_status,
        )

        return Response(
            {
                "success": True,
                "message": "Order saved.",
                "data": BTOrderReadSerializer(order).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ─── Retrieve ─────────────────────────────────────────────────────────────────

class BTOrderRetrieveView(views.APIView):
    """GET /api/v1/bqorders/<external_id>/"""
    permission_classes = [AllowAny]
    authentication_classes: list = []


    def get(self, request, external_id: str, *args, **kwargs):
        order = get_object_or_404(BTOrder, external_id=external_id)
        return Response(
            {"success": True, "data": BTOrderReadSerializer(order).data},
            status=status.HTTP_200_OK,
        )

# ─── BT webhook (API 8) ───────────────────────────────────────────────────────

class BTOrderWebhookView(views.APIView):
    """
    POST /api/v1/bqorders/webhook/

    BT pushes ProductOrderStateChangeEvent and related notifications here.
    We update bt_state on the matching order and always append a BTOrderEvent
    row — even when the order can't be found yet (race between order creation
    and the first webhook). Orphaned events are reconcilable later.

    Reply 200 quickly; BT retries on non-2xx.
    """
    permission_classes = [AllowAny]
    authentication_classes: list = []

    def post(self, request, *args, **kwargs):
        ser = BTWebhookSerializer(data=request.data)
        if not ser.is_valid():
            logger.warning("[bqorders webhook] Invalid payload: %s", ser.errors)
            # We still 200 — BT will not retry on 400, but we don't want to drop
            # genuinely-malformed events into the retry queue. Log and move on.
            return Response(
                {"status": 200, "message": "Invalid payload; logged."},
                status=status.HTTP_200_OK,
            )

        v = ser.validated_data
        po: dict[str, Any] = (v.get("event") or {}).get("productOrder") or {}
        external_id = po.get("externalId") or ""
        bt_order_id = po.get("id") or ""
        errors      = po.get("errorMessage") or []
        items       = po.get("productOrderItem") or []
        state       = (items[0].get("state") if items else "") or ""

        # First errorMessage subCode (for indexing)
        sub_code = ""
        first_msg = ""
        if isinstance(errors, list) and errors:
            first = errors[0] or {}
            sub_code  = str(first.get("subCode") or "")
            first_msg = str(first.get("message") or "")

        order = (
            BTOrder.objects.filter(external_id=external_id).first()
            or BTOrder.objects.filter(bt_order_id=bt_order_id).first()
        )

        if order:
            # Backfill bt_order_id if BT only had externalId when we created the row.
            if bt_order_id and (not order.bt_order_id or order.bt_order_id.startswith("PENDING-")):
                order.bt_order_id = bt_order_id

            if state and state in BTOrderState.values:
                order.advance_state(state, errors if errors else None)
            elif state:
                # Unknown but truthy state — log it on the order anyway.
                order.bt_state = state
                if errors:
                    order.advance_state(state, errors)
                else:
                    order.save(update_fields=["bt_state", "updated_at"])
            elif bt_order_id and order.bt_order_id != bt_order_id:
                order.save(update_fields=["bt_order_id", "updated_at"])

        BTOrderEvent.objects.create(
            order        = order,
            external_id  = external_id,
            source       = BTOrderEvent.Source.WEBHOOK,
            event_type   = v.get("eventType") or "",
            bt_event_id  = v.get("eventId") or "",
            state        = state,
            sub_code     = sub_code,
            message      = first_msg,
            payload_raw  = request.data if isinstance(request.data, dict) else {},
        )

        logger.info(
            "[bqorders webhook] event=%s external_id=%s bt_order_id=%s state=%s order_found=%s",
            v.get("eventType"), external_id, bt_order_id, state, bool(order),
        )

        return Response(
            {"status": 200, "message": "Notification received successfully"},
            status=status.HTTP_200_OK,
        )
