from django.contrib import admin
from django.utils.html import format_html

from .models import BTOrder, BTOrderEvent


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
        "external_id", "email", "product_offering_id",
        "local_status", "bt_state_badge", "total",
        "appointment_start", "created_at",
    )
    list_filter = ("local_status", "bt_state", "payment_method", "created_at")
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
        "cart_raw", "service_address_raw", "billing_address_raw",
        "shipping_address_raw", "totals_raw", "coupon_raw",
        "bt_response_raw", "request_payload_raw",
    )

    fieldsets = (
        ("Identity", {
            "fields": ("external_id", "bt_order_id", "local_status", "bt_state", "error_message"),
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
