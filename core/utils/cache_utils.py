from functools import wraps

from django.core.cache import cache


def cache_response(timeout=300, key_prefix=None):
    """
    DRY decorator for caching view queryset responses.

    :param timeout: cache duration in seconds (default 5 min)
    :param key_prefix: optional prefix for the cache key
    """

    def decorator(func):
        @wraps(func)
        def wrapper(view_instance, *args, **kwargs):
            user = getattr(view_instance.request, "user", None)
            # Build cache key: user-based for list views, pk-based for detail views
            key_parts = [key_prefix or func.__name__]
            if user and user.is_authenticated:
                key_parts.append(f"user_{user.id}")
            # Add kwargs if present (for detail views)
            for k, v in kwargs.items():
                key_parts.append(f"{k}_{v}")
            cache_key = "_".join(key_parts)

            # Try fetching from cache
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data

            # Compute result if not cached
            result = func(view_instance, *args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result

        return wrapper

    return decorator


def invalidate_cache(*keys):
    """
    Utility to delete multiple cache keys.
    """
    for key in keys:
        cache.delete(key)
