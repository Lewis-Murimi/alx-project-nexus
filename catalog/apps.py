from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalog'

    def ready(self):
        from .models import Product
        from core.utils.cache_signals import register_cache_invalidation

        # Automatically invalidate cache for products
        register_cache_invalidation(
            Product,
            list_cache_key_prefix="products_list",
            detail_cache_key_prefix="product_detail"
        )
