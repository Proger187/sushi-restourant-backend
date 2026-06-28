from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import Order
from .serializers import (
    AdminOrderSerializer,
    OrderCreateSerializer,
    OrderStatusSerializer,
    OrderStatusUpdateSerializer,
)


# --- Public ---

class OrderCreateView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = OrderCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
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
    queryset = Order.objects.prefetch_related("items")
    lookup_field = "id"


# --- Admin ---

class AdminOrderListView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminOrderSerializer

    def get_queryset(self):
        qs = Order.objects.prefetch_related("items")
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
    queryset = Order.objects.prefetch_related("items")
    lookup_field = "id"


class AdminOrderStatusUpdateView(UpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OrderStatusUpdateSerializer
    queryset = Order.objects.all()
    lookup_field = "id"
