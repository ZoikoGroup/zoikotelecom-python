from rest_framework import serializers


class CouponPreviewSerializer(serializers.Serializer):
    code = serializers.CharField()

class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    order_id = serializers.CharField()
    plan_id = serializers.IntegerField(required=False)
