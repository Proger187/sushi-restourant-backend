import os

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DeliveryZone
from .serializers import DeliveryCalculateInputSerializer, DeliveryZoneSerializer
from .utils import haversine


# --- Public ---

class DeliveryCalculateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DeliveryCalculateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        restaurant_lat = float(os.getenv("RESTAURANT_LAT", "0"))
        restaurant_lng = float(os.getenv("RESTAURANT_LNG", "0"))

        distance = haversine(
            restaurant_lat, restaurant_lng,
            serializer.validated_data["lat"],
            serializer.validated_data["lng"],
        )

        zone = (
            DeliveryZone.objects
            .filter(is_active=True, max_km__gte=distance)
            .order_by("max_km")
            .first()
        )

        if not zone:
            return Response({"available": False, "message": "Outside delivery area"})

        return Response({
            "available": True,
            "distance_km": round(distance, 2),
            "delivery_fee": str(zone.delivery_fee),
            "min_order_amount": str(zone.min_order_amount),
            "zone_name": zone.name,
        })


# --- Admin ---

class AdminDeliveryZoneListCreateView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DeliveryZoneSerializer
    queryset = DeliveryZone.objects.all()


class AdminDeliveryZoneUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = DeliveryZoneSerializer
    queryset = DeliveryZone.objects.all()
