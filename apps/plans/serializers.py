from rest_framework import serializers
from .models import Plan, PlanCategory, PlanVariation

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
            "is_active",
            "is_featured",
            "sort_order",
            "created_at",
            "updated_at",
            "variations",
        ]
