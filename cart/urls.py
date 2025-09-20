from django.urls import path
from .views import CartView, AddToCartView, UpdateCartItemView, RemoveFromCartView, ClearCartView

urlpatterns = [
    path("", CartView.as_view(), name="cart_detail"),
    path("add/", AddToCartView.as_view(), name="add_to_cart"),
    path("update/<int:pk>/", UpdateCartItemView.as_view(), name="update_cart_item"),
    path("remove/<int:pk>/", RemoveFromCartView.as_view(), name="remove_from_cart"),
    path("clear/", ClearCartView.as_view(), name="clear_cart"),
]