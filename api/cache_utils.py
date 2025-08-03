from django.core.cache import cache
from django.conf import settings
import hashlib


def get_cache_key(prefix, *args, **kwargs):
    """
    Generate a cache key based on prefix and arguments
    """
    key_parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        key_parts.append(str(arg))
    
    # Add keyword arguments (sorted for consistency)
    for key, value in sorted(kwargs.items()):
        key_parts.append(f"{key}:{value}")
    
    # Create a hash of the key parts to ensure it's not too long
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def invalidate_product_cache(product_id=None):
    """
    Invalidate product-related cache
    """
    if product_id:
        # Invalidate specific product cache
        cache.delete(f"product_detail_{product_id}")
        cache.delete(f"product_{product_id}")
    
    # Invalidate product list cache
    cache.delete_pattern("*products_list*")
    cache.delete_pattern("*product_list*")
    cache.delete_pattern("*public_products*")


def invalidate_category_cache(category_id=None):
    """
    Invalidate category-related cache
    """
    if category_id:
        # Invalidate specific category cache
        cache.delete(f"category_detail_{category_id}")
        cache.delete(f"category_{category_id}")
    
    # Invalidate category list cache
    cache.delete_pattern("*categories_list*")
    cache.delete_pattern("*category_list*")
    cache.delete_pattern("*public_categories*")


def invalidate_order_cache(order_id=None, user_id=None):
    """
    Invalidate order-related cache
    """
    if order_id:
        cache.delete(f"order_detail_{order_id}")
        cache.delete(f"order_{order_id}")
    
    if user_id:
        cache.delete(f"user_orders_{user_id}")
        cache.delete_pattern(f"*user_{user_id}_orders*")
    
    # Invalidate order list cache
    cache.delete_pattern("*orders_list*")
    cache.delete_pattern("*order_list*")


def cache_product_list(queryset, timeout=3600):
    """
    Cache product list with optimized queryset
    """
    cache_key = get_cache_key("products_list", timeout=timeout)
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        # Cache the queryset
        cached_data = list(queryset)
        cache.set(cache_key, cached_data, timeout)
    
    return cached_data


def cache_category_list(queryset, timeout=3600):
    """
    Cache category list with optimized queryset
    """
    cache_key = get_cache_key("categories_list", timeout=timeout)
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        # Cache the queryset
        cached_data = list(queryset)
        cache.set(cache_key, cached_data, timeout)
    
    return cached_data


def get_cached_product(product_id):
    """
    Get cached product by ID
    """
    cache_key = f"product_detail_{product_id}"
    return cache.get(cache_key)


def set_cached_product(product, timeout=3600):
    """
    Cache product data
    """
    cache_key = f"product_detail_{product.id}"
    cache.set(cache_key, product, timeout)


def get_cached_category(category_id):
    """
    Get cached category by ID
    """
    cache_key = f"category_detail_{category_id}"
    return cache.get(cache_key)


def set_cached_category(category, timeout=3600):
    """
    Cache category data
    """
    cache_key = f"category_detail_{category.id}"
    cache.set(cache_key, category, timeout)


def clear_all_cache():
    """
    Clear all cache (use with caution)
    """
    cache.clear()


def get_cache_stats():
    """
    Get cache statistics (if supported by backend)
    """
    try:
        # This is Redis-specific, may not work with other backends
        redis_client = cache.client.get_client()
        info = redis_client.info()
        return {
            'used_memory': info.get('used_memory_human', 'N/A'),
            'connected_clients': info.get('connected_clients', 'N/A'),
            'total_commands_processed': info.get('total_commands_processed', 'N/A'),
        }
    except Exception:
        return {'error': 'Cache stats not available'} 