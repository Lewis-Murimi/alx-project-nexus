from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters

from core.utils.cache_utils import cache_response, invalidate_cache
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

CACHE_TTL = 60 * 10  # 10 minutes


# Category Views
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


# Product Views
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category__id", "price"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at", "name"]
    ordering = ["name"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    @cache_response(timeout=300, key_prefix="products_list")
    def get_queryset(self):
        return Product.objects.select_related("category").all().order_by("-created_at")

    def perform_create(self, serializer):
        product = serializer.save()
        invalidate_cache("products_list")  # clear the cached list


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    @cache_response(timeout=300, key_prefix="product_detail")
    def get_queryset(self):
        return Product.objects.select_related("category").all()

    def perform_update(self, serializer):
        product = serializer.save()
        invalidate_cache(f"product_detail_{product.pk}", "products_list")

    def perform_destroy(self, instance):
        invalidate_cache(f"product_detail_{instance.pk}", "products_list")
        instance.delete()
