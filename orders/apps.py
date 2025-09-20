from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        from .models import Order
        from core.utils.cache_signals import register_cache_invalidation

        # Automatically invalidate cache for orders
        register_cache_invalidation(
            Order,
            list_cache_key_prefix="orders_list",
            detail_cache_key_prefix="order_detail"
        )
