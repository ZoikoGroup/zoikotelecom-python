from rest_framework import generics, filters
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch

from .models import Product, ProductCategory, ProductImage, ProductVariant, ProductVariantImage
from .serializers import ProductSerializer, ProductCategorySerializer
from .filters import ProductFilter


def _product_prefetches():
    """Shared prefetches, ordered so the 'main' image comes first for thumbnail use."""
    return [
        'attributes',
        Prefetch(
            'images',
            queryset=ProductImage.objects.order_by('-is_main', 'id'),
        ),
        Prefetch(
            'variants',
            queryset=ProductVariant.objects.prefetch_related(
                Prefetch(
                    'images',
                    queryset=ProductVariantImage.objects.order_by('-is_main', 'id'),
                )
            ),
        ),
    ]


# -----------------------------
# Product List API (With Filters)
# -----------------------------
class ProductListAPIView(generics.ListAPIView):
    queryset = (
        Product.objects
        .select_related('category')
        .prefetch_related(*_product_prefetches())
        .distinct()
        .all()
    )
    serializer_class = ProductSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'variants__regular_price']
    ordering = ['-created_at']


# -----------------------------
# Product Detail API
# -----------------------------
class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = (
        Product.objects
        .select_related('category')
        .prefetch_related(*_product_prefetches())
        .all()
    )
    serializer_class = ProductSerializer
    lookup_field = 'slug'


# -----------------------------
# Category List API
# -----------------------------
class CategoryListAPIView(generics.ListAPIView):
    queryset = ProductCategory.objects.filter(is_active=True)
    serializer_class = ProductCategorySerializer


# -----------------------------
# Optional ViewSet Version
# -----------------------------
class ProductViewSet(ReadOnlyModelViewSet):
    queryset = (
        Product.objects
        .select_related('category')
        .prefetch_related(*_product_prefetches())
        .distinct()
        .all()
    )
    serializer_class = ProductSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'variants__regular_price']
    ordering = ['-created_at']