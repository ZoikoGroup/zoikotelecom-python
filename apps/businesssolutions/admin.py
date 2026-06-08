from django.contrib import admin
from .models import BusinessSolution


@admin.register(BusinessSolution)
class BusinessSolutionAdmin(admin.ModelAdmin):

    list_display = (
        "full_name",
        "company",
        "email",
        "phone",
        "country",
        "service_interest",
        "status",
        "created_at",
    )

    search_fields = (
        "full_name",
        "company",
        "email",
        "phone",
    )

    list_filter = (
        "status",
        "country",
        "service_interest",
    )