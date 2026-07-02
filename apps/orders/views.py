from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Order, OrderItem, OrderStatusHistory
from .serializers import (
    AdminOrderSerializer,
    AdminOrderStatusUpdateSerializer,
    OrderCreateSerializer,
    OrderStatusSerializer,
)


def _order_prefetch():
    return [
        Prefetch("items", queryset=OrderItem.objects.select_related("product")),
        Prefetch("status_history", queryset=OrderStatusHistory.objects.order_by("changed_at")),
    ]


# --- Customer ---

@method_decorator(ratelimit(key="ip", rate="10/h", method="POST", block=True), name="dispatch")
class CustomerOrderListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCreateSerializer

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderStatusSerializer
        return OrderCreateSerializer

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related(*_order_prefetch())
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
    queryset = Order.objects.select_related("user").prefetch_related(
        Prefetch("items", queryset=OrderItem.objects.select_related("product")),
        "status_history",
    )
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
        qs = Order.objects.prefetch_related(*_order_prefetch()).select_related("user")
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
    queryset = Order.objects.select_related("user").prefetch_related(*_order_prefetch())
    lookup_field = "id"


class AdminOrderStatusUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, id):
        order = Order.objects.prefetch_related(*_order_prefetch()).get(pk=id)
        serializer = AdminOrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.set_status(
            serializer.validated_data["status"],
            changed_by=request.user.username,
            note=serializer.validated_data.get("note", ""),
        )
        order.refresh_from_db()
        return Response(AdminOrderSerializer(order).data)
