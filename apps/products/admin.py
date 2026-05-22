from django.contrib import admin
from django import forms
from django.utils.safestring  import mark_safe
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


# ---------------- VARIANT IMAGE INLINE ----------------
class ProductVariantImageInline(admin.TabularInline):
    model = ProductVariantImage
    extra = 1


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
            return mark_safe("<strong># {}</strong>", obj.pk)
        return "-"

    variant_id.short_description = "Variant ID"


# ---------------- CATEGORY ADMIN ----------------
@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "created_at"]
    search_fields = ["name"]
    list_filter = ["is_active"]
    prepopulated_fields = {"slug": ("name",)}



# ---------------- PRODUCT ADMIN ----------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fieldsets = (("General", {"fields": ("category", "name", "description", "slug")}),)

    inlines = [
        ProductImageInline,
        ProductAttributeInline,
        ProductVariantInline,
    ]


# ---------------- VARIANT ADMIN ----------------
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ["product", "storage", "colour", "condition"]
    search_fields = ["product__name"]
    list_filter = ["product"]

    # THIS enables multiple images per variant
    inlines = [ProductVariantImageInline]



# ---------------- PRODUCT IMAGE ADMIN ----------------
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["product", "image", "is_main"]
    list_filter = ["is_main"]
