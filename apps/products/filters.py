import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):

    category = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='iexact'
    )
    

    min_price = django_filters.NumberFilter(
        field_name='variants__regular_price',
        lookup_expr='gte'
    )


    max_price = django_filters.NumberFilter(
        field_name='variants__regular_price',
        lookup_expr='lte'
    )

    colour = django_filters.CharFilter(
        field_name='variants__colour',
        lookup_expr='iexact'
    )

    condition = django_filters.CharFilter(
        field_name='variants__condition',
        lookup_expr='iexact'
    )

    storage = django_filters.CharFilter(
        field_name='variants__storage',
        lookup_expr='iexact'
    )

    class Meta:
        model = Product
        fields = [
            'category',
            'min_price',
            'max_price',
            'colour',
            'condition',
            'storage',
        ]