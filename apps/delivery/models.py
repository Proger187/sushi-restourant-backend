import os
import uuid

from django.db import models


class DeliveryZone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    max_km = models.FloatField()
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["max_km"]

    def __str__(self):
        return self.name


class RestaurantSettings(models.Model):
    name = models.CharField(max_length=200, default="Sushi Restaurant")
    address = models.TextField(default="")
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    working_hours = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "restaurant settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "name": os.getenv("RESTAURANT_NAME", "Sushi Restaurant"),
                "address": os.getenv("RESTAURANT_ADDRESS", ""),
                "latitude": float(os.getenv("RESTAURANT_LAT", "51.1279")),
                "longitude": float(os.getenv("RESTAURANT_LNG", "71.4304")),
            },
        )
        return obj

    def __str__(self):
        return self.name
