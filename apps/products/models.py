from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
import uuid

class ProductCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(
        ProductCategory,
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    product = models.ForeignKey(
        Product, related_name="attributes", on_delete=models.CASCADE
    )
    storage = models.CharField(max_length=100)
    colour = models.CharField(max_length=100)
    condition = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Attribute"
        verbose_name_plural = "Attributes"

    def __str__(self):
        return (
            f"{self.product.name} - {self.storage} - {self.colour} - {self.condition}"
        )

class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, related_name="variants", on_delete=models.CASCADE
    )

    #  Store combination directly instead of FK
    storage = models.CharField(max_length=100)
    colour = models.CharField(max_length=100)
    condition = models.CharField(max_length=100)

    # image = models.ImageField(
    #     upload_to="variant_images/",
    #     null=True,
    #     blank=True
    # )

    regular_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )

    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0
    )

    stock_status = models.CharField(
        max_length=20,
        choices=[
            ("in_stock", "In Stock"),
            ("out_of_stock", "Out of Stock"),
        ],
        default="in_stock",
    )

    quantity = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        unique_together = ("product", "storage", "colour", "condition")

    def __str__(self):
        return f"{self.product.name} - {self.storage}/{self.colour}/{self.condition}"


class ProductVariantImage(models.Model):
    variant = models.ForeignKey(
        ProductVariant, related_name="images", on_delete=models.CASCADE
    )


    image = models.ImageField(upload_to="variant_images/")
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.variant} Image"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    # variant = models.ForeignKey(
    #     ProductVariant,
    #     related_name="images",
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True
    # )
    image = models.ImageField(upload_to="products/")
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} Image"
