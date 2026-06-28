from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.delivery.models import DeliveryZone

ZONES = [
    {"name": "Zone 1 — up to 3km", "max_km": 3, "delivery_fee": Decimal("0.00"), "min_order_amount": Decimal("30.00")},
    {"name": "Zone 2 — up to 4km", "max_km": 4, "delivery_fee": Decimal("2.00"), "min_order_amount": Decimal("40.00")},
    {"name": "Zone 3 — up to 6km", "max_km": 6, "delivery_fee": Decimal("3.00"), "min_order_amount": Decimal("50.00")},
    {"name": "Zone 4 — up to 7km", "max_km": 7, "delivery_fee": Decimal("4.00"), "min_order_amount": Decimal("60.00")},
    {"name": "Zone 5 — up to 9km", "max_km": 9, "delivery_fee": Decimal("5.00"), "min_order_amount": Decimal("80.00")},
    {"name": "Zone 6 — up to 10km", "max_km": 10, "delivery_fee": Decimal("5.00"), "min_order_amount": Decimal("90.00")},
]


class Command(BaseCommand):
    help = "Seed delivery zones"

    def handle(self, *args, **options):
        for zone_data in ZONES:
            obj, created = DeliveryZone.objects.update_or_create(
                max_km=zone_data["max_km"],
                defaults=zone_data,
            )
            status = "created" if created else "updated"
            self.stdout.write(f"  {status}: {obj.name}")
        self.stdout.write(self.style.SUCCESS(f"Done — {len(ZONES)} zones seeded"))
