from django.urls import path

from .views import (
    OrderListView,
    CheckoutView,
    OrderDetailView,
    CancelOrderView,
    UpdateOrderView,
    PayOrderView,
)

urlpatterns = [
    path("", OrderListView.as_view(), name="order_list"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("<int:pk>/cancel/", CancelOrderView.as_view(), name="cancel_order"),
    path("<int:pk>/update/", UpdateOrderView.as_view(), name="order-update"),
    path("<int:pk>/pay/", PayOrderView.as_view(), name="pay_order"),
]
