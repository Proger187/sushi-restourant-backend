from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser

from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)
from .utils import validate_image


# --- Public ---

class CategoryListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True)


class ProductListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer

    def get_queryset(self):
        qs = Product.objects.filter(is_available=True).select_related("category")
        category_slug = self.request.query_params.get("category")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if self.request.query_params.get("featured", "").lower() == "true":
            qs = qs.filter(is_featured=True)
        return qs


class ProductDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.select_related("category")
    lookup_field = "slug"


# --- Admin ---

class AdminCategoryListCreateView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        image = self.request.FILES.get("image")
        if image:
            validate_image(image)
        serializer.save()


class AdminCategoryUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = "slug"
    parser_classes = [MultiPartParser, FormParser]

    def perform_update(self, serializer):
        image = self.request.FILES.get("image")
        if image:
            validate_image(image)
        serializer.save()


class AdminProductListCreateView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.select_related("category")
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        image = self.request.FILES.get("image")
        if image:
            validate_image(image)
        serializer.save()


class AdminProductUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.select_related("category")
    lookup_field = "slug"
    parser_classes = [MultiPartParser, FormParser]

    def perform_update(self, serializer):
        image = self.request.FILES.get("image")
        if image:
            validate_image(image)
        serializer.save()
