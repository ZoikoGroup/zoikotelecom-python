from django.contrib import admin
from django import forms
from django.utils.safestring  import mark_safe
from django.utils.html  import format_html
from .models import (
    Product,
    ProductAttribute,
    ProductImage,
    ProductCategory,
    ProductVariant,
    ProductVariantImage,
)

# ---------------- ATTRIBUTE INLINE ----------------
class ProductAttributeInlineForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ["storage", "colour", "condition"]

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    form = ProductAttributeInlineForm
    extra = 0
    max_num = 1


# ---------------- PRODUCT IMAGE INLINE ----------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image", "is_main", "thumbnail_preview"]
    readonly_fields = ["thumbnail_preview"]

    def thumbnail_preview(self, obj):
        if obj.pk and obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" style="height:60px;width:60px;object-fit:cover;border-radius:4px;" />'
            )
        return "-"

    thumbnail_preview.short_description = "Preview"


# ---------------- VARIANT IMAGE INLINE ----------------
class ProductVariantImageInline(admin.TabularInline):
    model = ProductVariantImage
    extra = 1
    fields = ["image", "is_main", "thumbnail_preview"]
    readonly_fields = ["thumbnail_preview"]

    def thumbnail_preview(self, obj):
        if obj.pk and obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" style="height:60px;width:60px;object-fit:cover;border-radius:4px;" />'
            )
        return "-"

    thumbnail_preview.short_description = "Preview"


# ---------------- VARIANT INLINE INSIDE PRODUCT ----------------
class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 0
    show_change_link = True
    readonly_fields = ("variant_id",)

    fields = (
        "variant_id",
        "storage",
        "colour",
        "condition",
        "regular_price",
        "sale_price",
        "stock_status",
        "quantity",
    )

    def variant_id(self, obj):
        if obj.pk:
            return format_html("<strong># {}</strong>", obj.pk)
        return "-"

    variant_id.short_description = "Variant ID"


# ---------------- CATEGORY ADMIN ----------------
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "thumbnail_preview", "is_active", "created_at"]
    search_fields = ["name"]
    list_filter = ["is_active"]
    prepopulated_fields = {"slug": ("name",)}
    fields = ["name", "slug", "image", "is_active"]

    def thumbnail_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" style="height:40px;width:40px;object-fit:cover;border-radius:4px;" />'
            )
        return "-"

    thumbnail_preview.short_description = "Thumbnail"



# ---------------- PRODUCT ADMIN ----------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fieldsets = (("General", {"fields": ("category", "name", "description", "slug")}),)
    list_display = ["name", "category", "category_thumbnail", "thumbnail_preview"]
    list_filter = ["category"]
    search_fields = ["name"]

    inlines = [
        ProductImageInline,
        ProductAttributeInline,
        ProductVariantInline,
    ]

    def category_thumbnail(self, obj):
        if obj.category and obj.category.image:
            return mark_safe(
                f'<img src="{obj.category.image.url}" style="height:40px;width:40px;object-fit:cover;border-radius:4px;" />'
            )
        return "-"

    category_thumbnail.short_description = "Category Image"

    def thumbnail_preview(self, obj):
        main_image = obj.images.filter(is_main=True).first() or obj.images.first()
        if main_image:
            return mark_safe(
                f'<img src="{main_image.image.url}" style="height:40px;width:40px;object-fit:cover;border-radius:4px;" />'
            )
        return "-"

    thumbnail_preview.short_description = "Product Image"


# ---------------- VARIANT ADMIN ----------------
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ["product", "duration", "condition","regular_price", "sale_price"]
    search_fields = ["product__name"]
    list_filter = ["product"]

    # THIS enables multiple images per variant
    inlines = [ProductVariantImageInline]



# ProductImage is intentionally NOT registered as a standalone admin menu.
# Images are managed inline from the Product admin page (see ProductImageInline above).
