from django.db import models


class ResellerForm(models.Model):

    company_name = models.CharField(max_length=255)

    contact_name = models.CharField(max_length=255)

    position = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    email = models.EmailField()

    phone_number = models.CharField(max_length=50)

    company_website = models.URLField(
        blank=True,
        null=True
    )

    company_address = models.TextField()

    city = models.CharField(max_length=100)

    post_code = models.CharField(max_length=50)

    country = models.CharField(max_length=100)

    services = models.JSONField(default=list)

    declaration_one = models.BooleanField(default=False)

    declaration_two = models.BooleanField(default=False)

    full_name = models.CharField(max_length=255)

    digital_signature = models.CharField(max_length=255)

    signed_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "reseller_form"
        ordering = ["-created_at"]

    def __str__(self):
        return self.company_name