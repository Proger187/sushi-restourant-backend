from django.core.cache import cache


def invalidate_catalog_cache():
    """Clear all cached catalog pages when products/categories change."""
    try:
        cache.delete_pattern("*sushigarden*")
    except Exception:
        pass
