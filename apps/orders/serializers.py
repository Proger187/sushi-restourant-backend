from decimal import Decimal

from rest_framework import serializers

from apps.catalog.models import Product

from .models import Order, OrderItem


class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "customer_name", "phone", "email", "address",
            "latitude", "longitude", "delivery_km", "delivery_fee",
            "payment_method", "notes", "items",
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
        product_ids = [item["product"] for item in items_data]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

        subtotal = Decimal("0")
        for item in items_data:
            product = products[item["product"]]
            subtotal += product.price * item["quantity"]

        delivery_fee = validated_data.get("delivery_fee", Decimal("0")) or Decimal("0")
        order = Order.objects.create(
            **validated_data,
            subtotal=subtotal,
            total=subtotal + delivery_fee,
        )

        order_items = [
            OrderItem(
                order=order,
                product=products[item["product"]],
                product_name=products[item["product"]].name,
                quantity=item["quantity"],
                unit_price=products[item["product"]].price,
            )
            for item in items_data
        ]
        OrderItem.objects.bulk_create(order_items)

        return order


class OrderItemReadSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "quantity", "unit_price", "line_total"]


class OrderStatusSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "order_number", "status", "created_at", "total", "items"]


class AdminOrderSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]
