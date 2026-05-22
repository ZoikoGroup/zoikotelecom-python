from rest_framework import serializers
from .models import BundleRequest

class BundleRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BundleRequest
        fields = "__all__"

    # Field-level validation
    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits")
        if len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits")
        return value

    # Object-level validation
    def validate(self, data):
        if not data.get("name"):
            raise serializers.ValidationError({"name": "Name is required"})
        return data