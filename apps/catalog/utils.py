from django.conf import settings
from django.core.exceptions import ValidationError


def validate_image(image_file):
    max_size = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if image_file.size > max_size:
        raise ValidationError(
            f"Image size must be under {settings.MAX_IMAGE_SIZE_MB}MB"
        )

    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if (
        hasattr(image_file, "content_type")
        and image_file.content_type not in allowed_types
    ):
        raise ValidationError("Only JPEG, PNG, and WebP images are allowed")


def get_image_url(request, image_field):
    if not image_field:
        return None
    return request.build_absolute_uri(image_field.url)
