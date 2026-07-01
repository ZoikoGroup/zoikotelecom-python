from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class ProductReview(models.Model):
    """A customer review for a product (products live in apps.products)."""

    # Loose link by product id/slug so this app doesn't hard-depend on products.
    product_id   = models.PositiveIntegerField(db_index=True)
    product_slug = models.SlugField(max_length=255, blank=True, db_index=True)

    name   = models.CharField(max_length=120)
    email  = models.EmailField(blank=True)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1–5 stars",
    )
    comment = models.TextField(blank=True)

    is_approved = models.BooleanField(
        default=True,
        help_text="Only approved reviews are shown on the site.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product_id", "-created_at"]),
            models.Index(fields=["product_slug", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.name} · {self.rating}★ · product {self.product_id}"
