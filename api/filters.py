import django_filters
from django.db.models import Count
from .models import Product, Category, Order


class ProductFilter(django_filters.FilterSet):
    """
    Filter for Product model with advanced filtering options
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    
    # Price range filtering
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Stock filtering
    min_stock = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    max_stock = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    out_of_stock = django_filters.BooleanFilter(method='filter_out_of_stock')
    
    # Date filtering
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Active status
    is_active = django_filters.BooleanFilter()
    
    class Meta:
        model = Product
        fields = {
            'name': ['exact', 'icontains'],
            'description': ['icontains'],
            'category': ['exact'],
            'price': ['exact', 'gte', 'lte'],
            'stock': ['exact', 'gte', 'lte'],
            'is_active': ['exact'],
        }
    
    def filter_in_stock(self, queryset, name, value):
        """Filter products that are in stock"""
        if value:
            return queryset.filter(stock__gt=0)
        return queryset
    
    def filter_out_of_stock(self, queryset, name, value):
        """Filter products that are out of stock"""
        if value:
            return queryset.filter(stock=0)
        return queryset


class CategoryFilter(django_filters.FilterSet):
    """
    Filter for Category model
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    
    # Date filtering
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Products count filtering
    min_products = django_filters.NumberFilter(method='filter_min_products')
    max_products = django_filters.NumberFilter(method='filter_max_products')
    
    class Meta:
        model = Category
        fields = {
            'name': ['exact', 'icontains'],
            'description': ['icontains'],
        }
    
    def filter_min_products(self, queryset, name, value):
        """Filter categories with minimum number of products"""
        if value:
            return queryset.annotate(
                product_count=Count('products')
            ).filter(product_count__gte=value)
        return queryset
    
    def filter_max_products(self, queryset, name, value):
        """Filter categories with maximum number of products"""
        if value:
            return queryset.annotate(
                product_count=Count('products')
            ).filter(product_count__lte=value)
        return queryset


class OrderFilter(django_filters.FilterSet):
    """
    Filter for Order model
    """
    user = django_filters.NumberFilter()
    user_name = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=Order.STATUS_CHOICES)
    
    # Price range filtering
    min_total = django_filters.NumberFilter(field_name='total_price', lookup_expr='gte')
    max_total = django_filters.NumberFilter(field_name='total_price', lookup_expr='lte')
    
    # Date filtering
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Order
        fields = {
            'user': ['exact'],
            'status': ['exact'],
            'total_price': ['exact', 'gte', 'lte'],
            'created_at': ['exact', 'gte', 'lte'],
        } 