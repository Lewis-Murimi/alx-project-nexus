from celery import current_app as celery_app
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart
from core.utils.cache_utils import cache_response, invalidate_cache
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderUpdateSerializer, CheckoutOrderSerializer
from .tasks import send_order_confirmation_email

CACHE_TTL = 60 * 10  # 10 minutes


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["status", "payment_method"]
    ordering_fields = ["created_at", "total_price"]
    search_fields = ["shipping_address", "items__product__name"]
    ordering = ["-created_at"]

    @cache_response(timeout=CACHE_TTL, key_prefix="orders_list")
    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related("user").prefetch_related("items__product")
        return qs if user.is_staff else qs.filter(user=user)


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=CheckoutOrderSerializer,  # this makes Swagger show the body
        responses={201: OrderSerializer, 400: "Bad Request"},
    )
    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        if not cart.items.exists():
            return Response(
                {"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CheckoutOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = Order.objects.create(
            user=request.user,
            shipping_address=serializer.validated_data["shipping_address"],
            payment_method=serializer.validated_data["payment_method"],
        )

        total_price = 0
        for item in cart.items.all():
            if item.product.stock < item.quantity:
                return Response(
                    {"detail": f"Not enough stock for {item.product.name}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
            # Deduct stock
            item.product.stock -= item.quantity
            item.product.save()

            total_price += item.product.price * item.quantity

        order.total_price = total_price
        order.save()

        invalidate_cache(f"orders_list_user_{request.user.id}")

        try:
            if celery_app.conf.broker_url:  # worker available
                send_order_confirmation_email.delay(order.id)
            else:  # fallback
                send_order_confirmation_email(order.id)
        except Exception:
            # safety net if broker unreachable
            send_order_confirmation_email(order.id)
        # Clear cart
        cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @cache_response(timeout=CACHE_TTL, key_prefix="order_detail")
    def get_queryset(self):
        # short-circuit for swagger schema generation
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()

        user = self.request.user
        qs = Order.objects.select_related("user").prefetch_related("items__product")
        return qs if user.is_staff else qs.filter(user=user)


class UpdateOrderView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # short-circuit for swagger schema generation
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()

        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def patch(self, request, *args, **kwargs):
        """Allow partial updates for pending orders"""
        response = self.partial_update(request, *args, **kwargs)

        # Invalidate caches
        order_id = self.get_object().pk
        invalidate_cache(
            f"order_detail_{order_id}", f"orders_list_user_{request.user.id}"
        )

        return response


class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        try:
            if request.user.is_staff:
                order = Order.objects.get(pk=pk)
            else:
                order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if order.status == "cancelled":
            return Response(
                {"detail": "Order already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if order.status != "pending":
            return Response(
                {"detail": "Only pending orders can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # restore stock
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()

        order.status = "cancelled"
        order.save()

        # Invalidate caches
        invalidate_cache(
            f"order_detail_{order.pk}", f"orders_list_user_{request.user.id}"
        )

        return Response(
            {"detail": "Order cancelled successfully."}, status=status.HTTP_200_OK
        )


class PayOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if order.status != "pending":
            return Response(
                {"detail": "Only pending orders can be paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Here we would integrate a real payment gateway
        # For simulation, we mark as paid
        order.status = "paid"
        order.payment_status = "paid"
        order.save()

        # Invalidate caches
        invalidate_cache(
            f"order_detail_{order.pk}", f"orders_list_user_{request.user.id}"
        )

        return Response({"detail": "Payment successful."}, status=status.HTTP_200_OK)
