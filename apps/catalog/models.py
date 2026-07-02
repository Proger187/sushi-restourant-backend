import uuid

from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to="categories/", blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True)
    weight_g = models.PositiveIntegerField(
        null=True, blank=True, help_text="Weight in grams"
    )
    pieces = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of pieces"
    )
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    allergens = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category__sort_order", "name"]
        indexes = [
            models.Index(fields=["is_available", "category"]),
            models.Index(fields=["is_featured"]),
        ]

    def __str__(self):
        return self.name
