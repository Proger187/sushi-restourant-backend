from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import DestroyAPIView, ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.catalog.models import Product
from apps.orders.models import Order, OrderItem, OrderStatusHistory
from apps.orders.serializers import OrderStatusSerializer

from .models import Favourite
from .serializers import (
    CustomerLoginSerializer,
    CustomerProfileSerializer,
    CustomerRegisterSerializer,
    FavouriteSerializer,
)


class CustomerRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        refresh = RefreshToken.for_user(customer)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "customer": {
                    "id": str(customer.id),
                    "email": customer.email,
                    "full_name": customer.full_name,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class CustomerLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomerLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.validated_data["customer"]
        refresh = RefreshToken.for_user(customer)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "customer": {
                    "id": str(customer.id),
                    "email": customer.email,
                    "full_name": customer.full_name,
                },
            }
        )


class CustomerProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user


class CustomerOrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = (
            Order.objects
            .filter(user=request.user)
            .prefetch_related(
                Prefetch("items", queryset=OrderItem.objects.select_related("product")),
                Prefetch("status_history", queryset=OrderStatusHistory.objects.order_by("changed_at")),
            )
        )
        return Response(OrderStatusSerializer(orders, many=True).data)


class FavouriteListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavouriteSerializer

    def get_queryset(self):
        return (
            Favourite.objects
            .filter(customer=self.request.user)
            .select_related("product__category")
        )

    def create(self, request, *args, **kwargs):
        product_id = request.data.get("product")
        product = get_object_or_404(Product, pk=product_id, is_available=True)
        fav, created = Favourite.objects.get_or_create(
            customer=request.user, product=product
        )
        return Response(
            FavouriteSerializer(fav).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class FavouriteDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(
            Favourite,
            customer=self.request.user,
            product_id=self.kwargs["product_id"],
        )


class CustomerChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current = request.data.get("current_password", "")
        new = request.data.get("new_password", "")
        if not request.user.check_password(current):
            return Response(
                {"error": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(new) < 8:
            return Response(
                {"error": "New password must be at least 8 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.set_password(new)
        request.user.save()
        return Response({"message": "Password updated successfully."})
