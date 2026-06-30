from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .emails import send_order_notification
from .models import (
    BTOrder, BTOrderEvent, MailStatus, OrderType,
    EEMobileOrder, LandlineOrder,
)


class BTOrderEventInline(admin.TabularInline):
    model = BTOrderEvent
    extra = 0
    can_delete = False
    readonly_fields = (
        "source", "event_type", "bt_event_id", "state",
        "sub_code", "message", "received_at",
    )
    fields = readonly_fields
    ordering = ("-received_at",)


# ─── Shared base admin ──────────────────────────────────────────────────────────
# Not registered directly. The three registered admins below each filter the
# queryset to one order_type, giving separate "Broadband / EE Mobile / Landline"
# sections that all read from the single BTOrder table.

class BaseOrderAdmin(admin.ModelAdmin):
    search_fields = (
        "external_id", "bt_order_id", "email",
        "first_name", "last_name", "service_postcode",
        "service_address_id", "appointment_id",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    readonly_fields = (
        "external_id", "bt_order_id",
        "created_at", "updated_at",
        "mail_sent", "mail_sent_at", "mail_error",
        "cart_raw", "service_address_raw", "billing_address_raw",
        "shipping_address_raw", "totals_raw", "coupon_raw",
        "bt_response_raw", "request_payload_raw",
    )

    inlines = [BTOrderEventInline]
    actions = ["resend_notification_email"]

    # ── Badges ──────────────────────────────────────────────────────────────
    @admin.display(description="Mail", ordering="mail_status")
    def mail_state_badge(self, obj):
        if not obj.mail_required:
            return format_html('<span style="color:#999;">—</span>')
        if obj.mail_status == MailStatus.SENT:
            colour, label = "#0a0", "Sent"
        elif obj.mail_status == MailStatus.FAILED:
            colour, label = "#c33", "Mail not send"
        else:
            colour, label = "#c80", "Pending"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;">{}</span>',
            colour, label,
        )

    @admin.display(description="BT state", ordering="bt_state")
    def bt_state_badge(self, obj):
        colour = {
            "acknowledged": "#888", "inProgress": "#0a7", "held": "#c80",
            "completed": "#0a0", "refused": "#c33", "cancelled": "#666",
            "rejected": "#c33",
        }.get(obj.bt_state, "#bbb")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;">{}</span>',
            colour, obj.bt_state or "—",
        )

    # ── Resend notification email ─────────────────────────────────────────────
    @admin.action(description="Resend notification email (EE mobile / landline)")
    def resend_notification_email(self, request, queryset):
        sent = failed = skipped = 0
        for order in queryset:
            if not order.mail_required:
                skipped += 1
                continue
            ok, err = send_order_notification(order)
            order.mail_sent    = ok
            order.mail_status  = MailStatus.SENT if ok else MailStatus.FAILED
            order.mail_error   = "" if ok else (err or "Unknown error")
            order.mail_sent_at = timezone.now() if ok else order.mail_sent_at
            order.save(update_fields=[
                "mail_sent", "mail_status", "mail_error", "mail_sent_at", "updated_at",
            ])
            BTOrderEvent.objects.create(
                order=order, external_id=order.external_id,
                source=BTOrderEvent.Source.MANUAL, event_type="NotificationEmailResend",
                state="sent" if ok else "failed", message="" if ok else (err or ""),
            )
            sent += int(ok)
            failed += int(not ok)
        self.message_user(
            request,
            f"Notification email — sent: {sent}, failed: {failed}, skipped (broadband): {skipped}.",
        )


# ─── Broadband (BT Wholesale) ─────────────────────────────────────────────────

@admin.register(BTOrder)
class BroadbandOrderAdmin(BaseOrderAdmin):
    list_display = (
        "external_id", "email", "product_offering_id",
        "local_status", "bt_state_badge", "total",
        "appointment_start", "created_at",
    )
    list_filter = ("local_status", "bt_state", "payment_method", "created_at")

    fieldsets = (
        ("Identity", {
            "fields": ("order_type", "external_id", "bt_order_id", "local_status", "bt_state", "error_message"),
        }),
        ("Customer", {
            "fields": (
                "first_name", "last_name", "email", "phone", "company_name",
                ("billing_street", "billing_house_number"),
                ("billing_city", "billing_region"),
                ("billing_state", "billing_zip"),
            ),
        }),
        ("Service address", {
            "fields": (
                "service_address_id", "service_postcode",
                ("service_street_nr", "service_street_name"),
                ("service_city", "service_district"),
                "service_qualifier",
            ),
        }),
        ("Product", {
            "fields": (
                "product_name", "product_offering_id", "contract_term",
                ("download_speed", "upload_speed"),
            ),
        }),
        ("Appointment", {
            "fields": ("appointment_id", "appointment_start", "appointment_end"),
        }),
        ("Payment", {
            "fields": (
                ("subtotal", "discount", "total"), "currency",
                "payment_method", "agreed_to_terms",
                ("coupon_code", "coupon_type", "coupon_discount"),
                "client_created_at",
            ),
        }),
        ("Raw (audit only — do not edit)", {
            "classes": ("collapse",),
            "fields": (
                "cart_raw", "service_address_raw",
                "billing_address_raw", "shipping_address_raw",
                "totals_raw", "coupon_raw",
                "bt_response_raw", "request_payload_raw",
            ),
        }),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(order_type=OrderType.BROADBAND)


# ─── EE mobile / landline (shared layout) ─────────────────────────────────────

_NONBROADBAND_FIELDSETS = (
    ("Identity", {
        "fields": ("order_type", "external_id", "local_status", "error_message"),
    }),
    ("Customer", {
        "fields": (
            "first_name", "last_name", "email", "phone", "company_name",
            ("billing_street", "billing_house_number"),
            ("billing_city", "billing_region"),
            ("billing_state", "billing_zip"),
        ),
    }),
    ("Plan", {
        "fields": ("product_name", "contract_term", ("data_allowance", "sim_type")),
    }),
    ("Notification email", {
        "fields": (
            ("mail_required", "mail_status"),
            ("mail_sent", "mail_sent_at"),
            "mail_error",
        ),
    }),
    ("Payment", {
        "fields": (
            ("subtotal", "discount", "total"), "currency",
            "payment_method", "agreed_to_terms",
            ("coupon_code", "coupon_type", "coupon_discount"),
            "client_created_at",
        ),
    }),
    ("Raw (audit only — do not edit)", {
        "classes": ("collapse",),
        "fields": (
            "cart_raw", "billing_address_raw", "shipping_address_raw",
            "totals_raw", "coupon_raw", "request_payload_raw",
        ),
    }),
    ("Timestamps", {"fields": ("created_at", "updated_at")}),
)


@admin.register(EEMobileOrder)
class EEMobileOrderAdmin(BaseOrderAdmin):
    list_display = (
        "external_id", "email", "product_name",
        "data_allowance", "sim_type", "mail_state_badge",
        "total", "created_at",
    )
    list_filter = ("mail_status", "sim_type", "payment_method", "created_at")
    fieldsets = _NONBROADBAND_FIELDSETS

    def get_queryset(self, request):
        return super().get_queryset(request).filter(order_type=OrderType.EE_MOBILE)


@admin.register(LandlineOrder)
class LandlineOrderAdmin(BaseOrderAdmin):
    list_display = (
        "external_id", "email", "product_name",
        "mail_state_badge", "total", "created_at",
    )
    list_filter = ("mail_status", "payment_method", "created_at")
    fieldsets = _NONBROADBAND_FIELDSETS

    def get_queryset(self, request):
        return super().get_queryset(request).filter(order_type=OrderType.LANDLINE)


# ─── Events ───────────────────────────────────────────────────────────────────

@admin.register(BTOrderEvent)
class BTOrderEventAdmin(admin.ModelAdmin):
    list_display = ("received_at", "source", "event_type", "state", "external_id", "order")
    list_filter = ("source", "event_type", "state")
    search_fields = ("external_id", "bt_event_id", "message")
    readonly_fields = [f.name for f in BTOrderEvent._meta.fields]
    ordering = ("-received_at",)