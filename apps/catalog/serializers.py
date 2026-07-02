from rest_framework import serializers

from .models import Category, Product
from .utils import get_image_url


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request:
            data["image"] = get_image_url(request, instance.image)
        return data


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "price", "image",
            "weight_g", "pieces", "is_available", "is_featured", "category",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["category"] = {"id": instance.category_id, "name": instance.category.name}
        request = self.context.get("request")
        if request:
            data["image"] = get_image_url(request, instance.image)
        return data


class ProductDetailSerializer(ProductListSerializer):
    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ["description", "allergens"]
