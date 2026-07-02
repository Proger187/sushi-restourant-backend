import random
import uuid
from datetime import date

from django.conf import settings
from django.db import models
from django.utils import timezone


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        CONFIRMED = "confirmed"
        COOKING = "cooking"
        READY = "ready"
        DELIVERING = "delivering"
        COMPLETED = "completed"
        CANCELLED = "cancelled"

    class PaymentMethod(models.TextChoices):
        CASH = "cash"
        CARD_ON_DELIVERY = "card_on_delivery"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="orders",
    )
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    address = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    delivery_km = models.FloatField(null=True, blank=True)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    confirmed_at = models.DateTimeField(null=True, blank=True)
    cooking_started_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery_minutes = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["order_number"]),
        ]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = (
                f"ORD-{date.today().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            )
        super().save(*args, **kwargs)

    TIMESTAMP_MAP = {
        "confirmed": "confirmed_at",
        "cooking": "cooking_started_at",
        "ready": "ready_at",
        "delivering": "picked_up_at",
        "completed": "delivered_at",
        "cancelled": "cancelled_at",
    }

    def set_status(self, new_status, changed_by="system", note=""):
        OrderStatusHistory.objects.create(
            order=self, status=new_status,
            changed_by=changed_by, note=note,
        )
        ts_field = self.TIMESTAMP_MAP.get(new_status)
        if ts_field:
            setattr(self, ts_field, timezone.now())
        self.status = new_status
        update_fields = ["status", "updated_at"]
        if ts_field:
            update_fields.append(ts_field)
        self.save(update_fields=update_fields)


class OrderStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=30)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.CharField(max_length=100, blank=True, default="system")
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["changed_at"]
        indexes = [
            models.Index(fields=["order", "changed_at"]),
        ]

    def __str__(self):
        return f"{self.order.order_number} → {self.status}"


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT)
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def line_total(self):
        return self.quantity * self.unit_price
