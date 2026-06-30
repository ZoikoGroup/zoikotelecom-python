from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

class PlanCategory(models.Model):
    """Groups plans into categories (e.g., Basic, Professional, Enterprise)."""

    name = models.CharField(_("Name"), max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), max_length=120, unique=True, blank=True)
    description = models.TextField(_("Description"), blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    sort_order = models.PositiveIntegerField(_("Sort Order"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Plan Category")
        verbose_name_plural = _("Plan Categories")
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Plan(models.Model):
    """
    A plan product with general settings and  integration fields.
    Actual pricing/duration lives in PlanVariation.
    """

    category = models.ForeignKey(
        PlanCategory,
        on_delete=models.PROTECT,
        related_name="plans",
        verbose_name=_("Category"),
    )

    # General tab fields
    name = models.CharField(_("Plan Name"), max_length=200)
    slug = models.SlugField(_("Plan Slug"), max_length=220, unique=True, blank=True)
    bt_plan_id = models.CharField(
        _("BT Plan ID"),
        max_length=100,
        blank=True,
        help_text=_("Plan ID as registered in ."),
    )
    bt_plan_name = models.CharField(
        _(" BT Plan Name"),
        max_length=200,
        blank=True,
        help_text=_("Plan name as it appears in ."),
    )
    description = models.TextField(_("Description"), blank=True)

    # Speed (plan-level; does not change with contract length)
    download_speed = models.FloatField(
        _("Download Speed (Mbps)"),
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_("Average download speed in Mbps. e.g. 73.6"),
    )
    upload_speed = models.FloatField(
        _("Upload Speed (Mbps)"),
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text=_("Average upload speed in Mbps. e.g. 18.4"),
    )

    is_active = models.BooleanField(_("Active"), default=True)
    is_featured = models.BooleanField(_("Featured"), default=False)
    sort_order = models.PositiveIntegerField(_("Sort Order"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Plans")
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.category.name} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def default_variation(self):
        """Returns the default (or cheapest) variation."""
        return self.variations.filter(is_active=True).order_by("price").first()

    @property
    def speed_display(self):
        """Human-readable speed, e.g. '73.6/18.4 Mbps' or '76 Mbps'."""
        def fmt(value):
            # Show 76 (not 76.0) but keep 73.6 as-is.
            f = float(value)
            return str(int(f)) if f.is_integer() else str(round(f, 2))

        if self.download_speed and self.upload_speed:
            return f"{fmt(self.download_speed)}/{fmt(self.upload_speed)} Mbps"
        if self.download_speed:
            return f"{fmt(self.download_speed)} Mbps"
        return ""


class DurationUnit(models.TextChoices):
    DAY = "day", _("Day(s)")
    WEEK = "week", _("Week(s)")
    MONTH = "month", _("Month(s)")
    YEAR = "year", _("Year(s)")


class PlanVariation(models.Model):
    """
    A specific pricing/duration variant of a Plan.
    E.g.: Monthly $9.99 | Quarterly $24.99 | Annual $89.99
    """

    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name="variations",
        verbose_name=_("Plan"),
    )

    label = models.CharField(
        _("Label"),
        max_length=100,
        help_text=_('Human-readable label, e.g. "Monthly", "Annual", "6-Month".'),
    )

    # Duration
    duration_value = models.PositiveIntegerField(
        _("Duration"),
        default=1,
        validators=[MinValueValidator(1)],
        help_text=_("Numeric duration value."),
    )
    duration_unit = models.CharField(
        _("Duration Unit"),
        max_length=10,
        choices=DurationUnit.choices,
        default=DurationUnit.MONTH,
    )

    # Pricing
    price = models.DecimalField(
        _("Price"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    
    sale_price = models.DecimalField(
            max_digits=10,
            decimal_places=2,
            null=True,
            blank=True,
            validators=[MinValueValidator(0)],
            help_text="Optional sale price (overrides regular price)"
        )
    
    price = models.DecimalField(max_digits=10, decimal_places=2)

    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    @property
    def final_price(self):
        return self.sale_price if self.sale_price else self.price
    #  variation-level fields (can override plan-level)
    bt_plan_id = models.CharField(
        _("BT Plan ID"),
        max_length=100,
        blank=True,
        help_text=_(
            "Leave blank to inherit from the parent plan. "
            "Set this if  has a separate plan per variation."
        ),
    )

    is_active = models.BooleanField(_("Active"), default=True)
    is_default = models.BooleanField(
        _("Default Variation"),
        default=False,
        help_text=_("Mark as the recommended/default option for this plan."),
    )
    sort_order = models.PositiveIntegerField(_("Sort Order"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Plan Variation")
        verbose_name_plural = _("Plan Variations")
        ordering = ["sort_order", "price"]

    def __str__(self):
        return f"{self.plan.name} — {self.label} ({self.duration_value} {self.get_duration_unit_display()})"

    @property
    def effective_bt_plan_id(self):
        """Return variation-level BT plan ID or fall back to parent plan."""
        return self.bt_plan_id or self.plan.bt_plan_id

    @property
    def discounted_price(self):
        return self.sale_price if self.sale_price is not None else self.price

    @property
    def duration_display(self):
        return f"{self.duration_value} {self.get_duration_unit_display()}"


class PlanFeature(models.Model):
    """
    A single feature/benefit line shown on a Plan.
    Admins can add as many features as they like per plan.
    """

    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name="features",
        verbose_name=_("Plan"),
    )
    text = models.CharField(
        _("Feature"),
        max_length=255,
        help_text=_('A feature/benefit line, e.g. "No Long-Term Contracts".'),
    )
    is_active = models.BooleanField(_("Active"), default=True)
    sort_order = models.PositiveIntegerField(_("Sort Order"), default=0)

    class Meta:
        verbose_name = _("Plan Feature")
        verbose_name_plural = _("Plan Features")
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.plan.name} — {self.text}"