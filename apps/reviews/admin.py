from django.contrib import admin
from django.utils.html import format_html
from .models import ProductReview


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("stars", "name", "product_id", "product_slug", "short_comment", "is_approved", "created_at")
    list_filter = ("is_approved", "rating", "created_at")
    search_fields = ("name", "email", "comment", "product_slug", "product_id")
    list_editable = ("is_approved",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    @admin.display(description="Rating", ordering="rating")
    def stars(self, obj):
        return format_html('<span style="color:#f5a623;font-size:14px;">{}</span>',
                           "★" * obj.rating + "☆" * (5 - obj.rating))

    @admin.display(description="Comment")
    def short_comment(self, obj):
        return (obj.comment[:60] + "…") if len(obj.comment or "") > 60 else obj.comment
