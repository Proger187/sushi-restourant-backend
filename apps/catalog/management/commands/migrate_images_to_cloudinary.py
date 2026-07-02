from pathlib import Path

from django.conf import settings
from django.core.files.base import File
from django.core.management.base import BaseCommand

from apps.catalog.models import Category, Product


class Command(BaseCommand):
    help = (
        "Upload existing local product/category images (from MEDIA_ROOT) to "
        "Cloudinary and repoint each model's image field at the uploaded copy. "
        "Requires CLOUDINARY_URL to be set in .env. Safe to re-run - skips "
        "instances whose image field no longer points at a local file."
    )

    def handle(self, *args, **options):
        local_media_root = Path(settings.MEDIA_ROOT)
        total_uploaded = 0
        total_skipped = 0
        total_failed = 0

        for model in (Category, Product):
            for instance in model.objects.exclude(image=""):
                local_path = local_media_root / instance.image.name
                if not local_path.is_file():
                    total_skipped += 1
                    continue

                relative_name = instance.image.name
                try:
                    with open(local_path, "rb") as fh:
                        instance.image.save(
                            Path(relative_name).name, File(fh), save=True
                        )
                except Exception as exc:
                    total_failed += 1
                    self.stderr.write(
                        self.style.ERROR(
                            f"{model.__name__} {instance.pk} ({relative_name}): {exc}"
                        )
                    )
                    continue

                total_uploaded += 1
                self.stdout.write(
                    f"{model.__name__} {instance.pk}: {relative_name} -> {instance.image.url}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Uploaded {total_uploaded}, skipped {total_skipped} "
                f"(no local file), failed {total_failed}."
            )
        )
