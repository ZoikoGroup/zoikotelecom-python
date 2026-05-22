from django.db import models


class BundleRequest(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    email = models.EmailField(blank=True, null=True)
    bundle_name = models.CharField(max_length=100)
    bundle_price = models.CharField(max_length=50)
    is_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.bundle_name}"