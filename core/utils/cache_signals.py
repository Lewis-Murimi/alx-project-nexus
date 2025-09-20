# core/utils/cache_signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .cache_utils import invalidate_cache


def register_cache_invalidation(model_class, list_cache_key_prefix=None, detail_cache_key_prefix=None):
    """
    Automatically invalidate cache when a model instance is created/updated/deleted.

    Args:
        model_class: Django model class to observe
        list_cache_key_prefix: Prefix used for cached list view
        detail_cache_key_prefix: Prefix used for cached detail view
    """

    @receiver([post_save, post_delete], sender=model_class)
    def clear_cache(sender, instance, **kwargs):
        # Invalidate detail cache
        if detail_cache_key_prefix:
            invalidate_cache(f"{detail_cache_key_prefix}_{instance.pk}")

        # Invalidate list cache
        if list_cache_key_prefix:
            # If user-specific cache
            if hasattr(instance, 'user_id'):
                invalidate_cache(f"{list_cache_key_prefix}_user_{instance.user_id}")
            else:
                invalidate_cache(f"{list_cache_key_prefix}")
