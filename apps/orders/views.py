from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Order
from .serializers import (
    AdminOrderSerializer,
    AdminOrderStatusUpdateSerializer,
    OrderCreateSerializer,
    OrderStatusSerializer,
)


# --- Customer ---

class CustomerOrderListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCreateSerializer

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderStatusSerializer
        return OrderCreateSerializer

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items", "status_history")
        )

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            {
                "id": str(order.id),
                "order_number": order.order_number,
                "status": order.status,
            },
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = OrderStatusSerializer
    queryset = Order.objects.prefetch_related("items", "status_history")
    lookup_field = "id"


class CustomerConfirmDeliveryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        order = get_object_or_404(Order, pk=id, user=request.user)
        if order.status != "delivering":
            return Response(
                {"error": "Can only confirm delivery when order is being delivered."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.set_status("completed", changed_by="customer")
        order.refresh_from_db()
        return Response(OrderStatusSerializer(order).data)


# --- Admin ---

class AdminOrderListView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminOrderSerializer

    def get_queryset(self):
        qs = Order.objects.prefetch_related("items", "status_history")
        order_status = self.request.query_params.get("status")
        if order_status:
            qs = qs.filter(status=order_status)
        date = self.request.query_params.get("date")
        if date:
            qs = qs.filter(created_at__date=date)
        return qs


class AdminOrderDetailView(RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminOrderSerializer
    queryset = Order.objects.prefetch_related("items", "status_history")
    lookup_field = "id"


class AdminOrderStatusUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, id):
        order = Order.objects.prefetch_related("items", "status_history").get(pk=id)
        serializer = AdminOrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.set_status(
            serializer.validated_data["status"],
            changed_by=request.user.username,
            note=serializer.validated_data.get("note", ""),
        )
        order.refresh_from_db()
        return Response(AdminOrderSerializer(order).data)
