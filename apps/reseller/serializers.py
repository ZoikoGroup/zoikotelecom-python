from rest_framework import serializers
from .models import ResellerApplication

class ResellerApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResellerApplication
        fields = '__all__'
