from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'subtitle',
            'positions',
            'experience',
            'location',
            'status',
            'description',
            'salary',
            'posted_by',
            'posted_at',
        ]
