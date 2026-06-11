from django.contrib import admin
from .models import ResellerForm


@admin.register(ResellerForm)
class ResellerFormAdmin(admin.ModelAdmin):

    list_display = (
        "company_name",
        "contact_name",
        "email",
        "phone_number",
        "country",
        "created_at",
    )

    search_fields = (
        "company_name",
        "contact_name",
        "email",
    )

    list_filter = (
        "country",
        "created_at",
    )