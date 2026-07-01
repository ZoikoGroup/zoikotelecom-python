from rest_framework import serializers
from .models import ProductReview


class ReviewReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ["id", "name", "rating", "comment", "created_at"]


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ["product_id", "product_slug", "name", "email", "rating", "comment"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
