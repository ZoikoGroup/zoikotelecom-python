from rest_framework import serializers
from .models import (
    Product,
    ProductAttribute,
    ProductImage,
    ProductCategory,
    ProductVariant,
    ProductVariantImage
)


# -----------------------------
# Variant Image Serializer
# -----------------------------
class ProductVariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantImage
        fields = ['id', 'image', 'is_main']


# -----------------------------
# Product Image Serializer
# -----------------------------
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main']


# -----------------------------
# Product Attribute Serializer
# -----------------------------
class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ['id', 'colour', 'condition', 'storage']


# -----------------------------
# Product Variant Serializer
# -----------------------------
class ProductVariantsSerializer(serializers.ModelSerializer):
    images = ProductVariantImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id',
            'storage',
            'colour',
            'condition',
            'regular_price',
            'sale_price',
            'stock_status',
            'quantity',
            'images'
        ]


# -----------------------------
# Category Serializer
# -----------------------------
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug']


# -----------------------------
# Product Serializer
# -----------------------------
class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    attributes = ProductAttributeSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantsSerializer(many=True, read_only=True)
    
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'slug',
            'category',
            'attributes',
            'images',
            'variants',
            'created_at',
            'updated_at'
        ]