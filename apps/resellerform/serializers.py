from rest_framework import serializers
from .models import ResellerForm


class ResellerFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = ResellerForm
        fields = "__all__"

    def validate(self, attrs):

        required_services = attrs.get("services", [])

        if not required_services:
            raise serializers.ValidationError(
                "Please select at least one service."
            )

        if not attrs.get("declaration_one"):
            raise serializers.ValidationError(
                "First declaration must be accepted."
            )

        if not attrs.get("declaration_two"):
            raise serializers.ValidationError(
                "Second declaration must be accepted."
            )

        return attrs