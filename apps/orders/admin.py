from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .emails import send_order_notification
from .models import BTOrder, BTOrderEvent, MailStatus


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

@admin.register(BTOrder)
class BTOrderAdmin(admin.ModelAdmin):
    list_display = (
        "external_id", "order_type", "email", "product_offering_id",
        "local_status", "bt_state_badge", "mail_state_badge", "total",
        "appointment_start", "created_at",
    )
    list_filter = ("order_type", "local_status", "bt_state", "mail_status", "payment_method", "created_at")
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

    fieldsets = (
        ("Identity", {
            "fields": ("order_type", "external_id", "bt_order_id", "local_status", "bt_state", "error_message"),
        }),
        ("Customer", {
            "fields": (
                "first_name", "last_name", "email", "phone", "company_name",
                ("billing_street", "billing_house_number"),
                ("billing_city",   "billing_region"),
                ("billing_state",  "billing_zip"),
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
                ("data_allowance", "sim_type"),
            ),
        }),
        ("Notification email", {
            "fields": (
                ("mail_required", "mail_status"),
                ("mail_sent", "mail_sent_at"),
                "mail_error",
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

    inlines = [BTOrderEventInline]

    actions = ["resend_notification_email"]

    # Coloured badge for the notification-email column.
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

    @admin.action(description="Resend notification email (EE mobile / landline)")
    def resend_notification_email(self, request, queryset):
        sent = 0
        failed = 0
        skipped = 0
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

    # Coloured badge for at-a-glance state filtering in the list view
    @admin.display(description="BT state", ordering="bt_state")
    def bt_state_badge(self, obj):
        colour = {
            "acknowledged": "#888",
            "inProgress":   "#0a7",
            "held":         "#c80",
            "completed":    "#0a0",
            "refused":      "#c33",
            "cancelled":    "#666",
            "rejected":     "#c33",
        }.get(obj.bt_state, "#bbb")
        label = obj.bt_state or "—"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;">{}</span>',
            colour, label,
        )

@admin.register(BTOrderEvent)
class BTOrderEventAdmin(admin.ModelAdmin):
    list_display = ("received_at", "source", "event_type", "state", "external_id", "order")
    list_filter = ("source", "event_type", "state")
    search_fields = ("external_id", "bt_event_id", "message")
    readonly_fields = [f.name for f in BTOrderEvent._meta.fields]
    ordering = ("-received_at",)
