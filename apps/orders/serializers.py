from decimal import Decimal

from rest_framework import serializers

from apps.catalog.models import Product

from .models import Order, OrderItem, OrderStatusHistory


class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)
    estimated_delivery_minutes = serializers.IntegerField(required=False)

    class Meta:
        model = Order
        fields = [
            "customer_name", "phone", "address",
            "latitude", "longitude", "delivery_km", "delivery_fee",
            "payment_method", "notes", "items", "estimated_delivery_minutes",
        ]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        product_ids = [item["product"] for item in value]
        products = Product.objects.filter(id__in=product_ids, is_available=True)
        if products.count() != len(product_ids):
            raise serializers.ValidationError(
                "One or more products do not exist or are unavailable."
            )
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        estimated_minutes = validated_data.pop("estimated_delivery_minutes", None)
        user = self.context["request"].user
        product_ids = [item["product"] for item in items_data]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

        subtotal = Decimal("0")
        for item in items_data:
            subtotal += products[item["product"]].price * item["quantity"]

        delivery_fee = validated_data.get("delivery_fee", Decimal("0")) or Decimal("0")
        order = Order.objects.create(
            **validated_data,
            user=user,
            subtotal=subtotal,
            total=subtotal + delivery_fee,
            estimated_delivery_minutes=estimated_minutes,
        )

        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=products[item["product"]],
                product_name=products[item["product"]].name,
                quantity=item["quantity"],
                unit_price=products[item["product"]].price,
            )
            for item in items_data
        ])

        order.set_status("pending", changed_by="customer")
        return order


class OrderItemReadSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "quantity", "unit_price", "line_total"]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = "__all__"


class OrderStatusSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "status", "created_at", "total",
            "delivery_fee", "subtotal", "customer_name", "phone",
            "address", "payment_method", "notes",
            "items", "status_history",
            "confirmed_at", "cooking_started_at", "ready_at",
            "picked_up_at", "delivered_at", "estimated_delivery_minutes",
        ]


class AdminOrderSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class AdminOrderStatusUpdateSerializer(serializers.Serializer):
    ADMIN_ALLOWED = [
        c for c in Order.Status.choices if c[0] != "completed"
    ]
    status = serializers.ChoiceField(choices=ADMIN_ALLOWED)
    note = serializers.CharField(required=False, default="", allow_blank=True)
