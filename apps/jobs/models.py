from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):

    STATUS_CHOICES = (
        (True, 'Active'),
        (False, 'Inactive'),
    )

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)

    positions = models.PositiveIntegerField(
        help_text="Number of open positions"
    )

    experience = models.CharField(
        max_length=100,
        help_text="e.g. 0-2 years, 3+ years"
    )

    location = models.CharField(max_length=100)

    status = models.BooleanField(
        default=True,
        choices=STATUS_CHOICES
    )

    description = models.TextField()

    salary = models.CharField(
        max_length=100,
        blank=True
    )

    posted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="jobs"
    )

    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.location}"
