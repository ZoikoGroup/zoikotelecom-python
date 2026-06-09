from django.db import models


class BusinessSolution(models.Model):

    SERVICE_CHOICES = (
    ("business_mobile", "Business Mobile"),
    ("business_broadband", "Business Broadband"),
    ("hosted_voice", "Hosted Voice"),
    ("full_fibre", "Full Fibre"),
    ("number_porting", "Number Porting"),
    ("managed_connectivity", "Managed Connectivity"),
    ("other", "Other")
    )

    full_name = models.CharField(max_length=255)

    company = models.CharField(
        max_length=255,
        blank=True
    )

    email = models.EmailField()

    phone = models.CharField(max_length=50)

    country = models.CharField(max_length=100)

    service_interest = models.CharField(
        max_length=100,
        choices=SERVICE_CHOICES
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    consent = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=(
            ("new", "New"),
            ("contacted", "Contacted"),
            ("closed", "Closed"),
        ),
        default="new"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.full_name