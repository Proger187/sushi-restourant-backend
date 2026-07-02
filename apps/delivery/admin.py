from django.contrib import admin

from .models import DeliveryZone, RestaurantSettings


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ["name", "max_km", "delivery_fee", "min_order_amount", "is_active"]


@admin.register(RestaurantSettings)
class RestaurantSettingsAdmin(admin.ModelAdmin):
    list_display = ["name", "address", "latitude", "longitude", "phone"]
