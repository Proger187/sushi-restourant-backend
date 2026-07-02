import logging

from django.conf import settings as django_settings
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DeliveryZone, RestaurantSettings
from .serializers import (
    DeliveryCalculateInputSerializer,
    DeliveryZoneSerializer,
    RestaurantSettingsSerializer,
)
from .utils import estimate_minutes, haversine

DELIVERY_ZONES_CACHE_KEY = "delivery_zones_active"


def get_active_zones():
    zones = cache.get(DELIVERY_ZONES_CACHE_KEY)
    if zones is None:
        zones = list(DeliveryZone.objects.filter(is_active=True).order_by("max_km"))
        cache.set(DELIVERY_ZONES_CACHE_KEY, zones, 60 * 30)
    return zones


def invalidate_zone_cache():
    cache.delete(DELIVERY_ZONES_CACHE_KEY)

logger = logging.getLogger(__name__)


# --- Public ---

class DeliveryCalculateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DeliveryCalculateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        restaurant = RestaurantSettings.get()
        restaurant_lat = restaurant.latitude
        restaurant_lng = restaurant.longitude

        lat = serializer.validated_data["lat"]
        lng = serializer.validated_data["lng"]

        logger.warning(
            "[Delivery] Restaurant: %s,%s | Customer: %s,%s",
            restaurant_lat, restaurant_lng, lat, lng,
        )

        distance = haversine(restaurant_lat, restaurant_lng, lat, lng)
        logger.warning("[Delivery] Distance: %.3f km", distance)

        zones = get_active_zones()
        if not zones:
            logger.error(
                "[Delivery] NO ACTIVE ZONES — run 'python manage.py seed_zones'"
            )

        zone = next(
            (z for z in zones if z.max_km >= distance),
            None,
        )

        if not zone:
            return Response({
                "available": False,
                "distance_km": round(distance, 2),
                "message": "Outside delivery area",
            })

        return Response({
            "available": True,
            "distance_km": round(distance, 2),
            "delivery_fee": str(zone.delivery_fee),
            "min_order_amount": str(zone.min_order_amount),
            "zone_name": zone.name,
            "estimated_minutes": estimate_minutes(distance),
        })


@method_decorator(cache_page(60 * 60), name="dispatch")
class PublicRestaurantSettingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        settings_obj = RestaurantSettings.get()
        return Response(RestaurantSettingsSerializer(settings_obj).data)


# --- Admin ---

class AdminRestaurantSettingsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        settings_obj = RestaurantSettings.get()
        return Response(RestaurantSettingsSerializer(settings_obj).data)

    def patch(self, request):
        settings_obj = RestaurantSettings.get()
        serializer = RestaurantSettingsSerializer(
            settings_obj, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        from apps.catalog.cache_utils import invalidate_catalog_cache
        invalidate_catalog_cache()
        return Response(serializer.data)


class AdminTestDeliveryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        if not django_settings.DEBUG:
            return Response({"error": "Only available in DEBUG mode"}, status=403)

        try:
            lat = float(request.query_params.get("lat", 0))
            lng = float(request.query_params.get("lng", 0))
        except (TypeError, ValueError):
            return Response({"error": "Invalid coordinates"}, status=400)

        restaurant = RestaurantSettings.get()
        distance = haversine(restaurant.latitude, restaurant.longitude, lat, lng)
        zones = list(
            DeliveryZone.objects.filter(is_active=True)
            .values("name", "max_km", "delivery_fee")
        )
        matched = (
            DeliveryZone.objects
            .filter(is_active=True, max_km__gte=distance)
            .order_by("max_km")
            .first()
        )

        return Response({
            "restaurant": {
                "lat": restaurant.latitude,
                "lng": restaurant.longitude,
            },
            "customer": {"lat": lat, "lng": lng},
            "distance_km": round(distance, 3),
            "active_zones": zones,
            "matched_zone": matched.name if matched else None,
        })


class PublicDeliveryZoneListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        zones = DeliveryZone.objects.filter(is_active=True).order_by("max_km")
        serializer = DeliveryZoneSerializer(zones, many=True)
        return Response(serializer.data)


class AdminDeliveryZoneListCreateView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DeliveryZoneSerializer
    queryset = DeliveryZone.objects.all()

    def perform_create(self, serializer):
        serializer.save()
        invalidate_zone_cache()


class AdminDeliveryZoneUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DeliveryZoneSerializer
    queryset = DeliveryZone.objects.all()

    def perform_update(self, serializer):
        serializer.save()
        invalidate_zone_cache()

    def perform_destroy(self, instance):
        instance.delete()
        invalidate_zone_cache()
