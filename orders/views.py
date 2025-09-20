from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderUpdateSerializer, CheckoutOrderSerializer
from cart.models import Cart, CartItem
from catalog.models import Product


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ["status", "payment_method"]
    ordering_fields = ["created_at", "total_price"]
    search_fields = ["shipping_address", "items__product__name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        if not cart.items.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

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

        # Clear cart
        cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow a user to view their own orders
        return Order.objects.filter(user=self.request.user)

class UpdateOrderView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def patch(self, request, *args, **kwargs):
        """Allow partial updates for pending orders"""
        return self.partial_update(request, *args, **kwargs)

class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        try:
            if request.user.is_staff:
                order = Order.objects.get(pk=pk)
            else:
                order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if order.status == "cancelled":
            return Response({"detail": "Order already cancelled."}, status=status.HTTP_400_BAD_REQUEST)

        if order.status != "pending":
            return Response(
                {"detail": "Only pending orders can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # restore stock
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()

        order.status = "cancelled"
        order.save()

        return Response({"detail": "Order cancelled successfully."}, status=status.HTTP_200_OK)