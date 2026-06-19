from django.db import models

class ResellerApplication(models.Model):
    company_name = models.CharField(max_length=150)
    contact_name = models.CharField(max_length=150)
    position = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    website = models.CharField(max_length=255, blank=True, null=True)
    
    address = models.TextField()
    city = models.CharField(max_length=100)
    post_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    services_of_interest = models.JSONField(default=list)
    
    full_name = models.CharField(max_length=150)
    digital_signature = models.CharField(max_length=150)
    signature_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Reseller Application"
        verbose_name_plural = "Reseller Applications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company_name} - {self.contact_name}"
