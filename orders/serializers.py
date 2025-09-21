from rest_framework import serializers

from catalog.serializers import ProductSerializer
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price", "subtotal"]

    def get_subtotal(self, obj):
        return obj.quantity * obj.price


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "shipping_address",
            "payment_method",
            "total_price",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "total_price", "status", "created_at", "updated_at"]


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["shipping_address", "payment_method"]

    def validate(self, attrs):
        if self.instance and self.instance.status != "pending":
            raise serializers.ValidationError("Only pending orders can be updated.")
        return attrs


class CheckoutOrderSerializer(serializers.ModelSerializer):
    """Serializer specifically for checkout where shipping_address and payment_method are required."""

    class Meta:
        model = Order
        fields = ["shipping_address", "payment_method"]

    def validate_shipping_address(self, value):
        if not value:
            raise serializers.ValidationError("Shipping address is required.")
        return value

    def validate_payment_method(self, value):
        if not value:
            raise serializers.ValidationError("Payment method is required.")
        return value
