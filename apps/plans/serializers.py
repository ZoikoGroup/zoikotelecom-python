from rest_framework import serializers
from .models import Plan, PlanCategory, PlanVariation, PlanFeature

class PlanFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanFeature
        fields = ["id", "text", "sort_order"]


class PlanVariationSerializer(serializers.ModelSerializer):
    duration_display = serializers.ReadOnlyField()
    effective_bt_plan_id = serializers.ReadOnlyField()
    
    

    class Meta:
        model = PlanVariation
        fields = [
            "id",
            "label",
            "duration_value",
            "duration_unit",
            "duration_display",
            "price",
            "sale_price",
            "bt_plan_id",
            "effective_bt_plan_id",
            "is_default",
            "is_active",
            "sort_order",
        ]


class PlanCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "is_active",
            "sort_order",
        ]


class PlanSerializer(serializers.ModelSerializer):
    variations = PlanVariationSerializer(many=True, read_only=True)
    category = PlanCategorySerializer(read_only=True)
    speed_display = serializers.ReadOnlyField()
    features = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "bt_plan_id",
            "bt_plan_name",
            "description",
            "download_speed",
            "upload_speed",
            "speed_display",
            "is_active",
            "is_featured",
            "sort_order",
            "created_at",
            "updated_at",
            "features",
            "variations",
        ]

    def get_features(self, obj):
        active_features = obj.features.filter(is_active=True).order_by(
            "sort_order", "id"
        )
        return PlanFeatureSerializer(active_features, many=True).data
