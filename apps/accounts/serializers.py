from django.contrib.auth import authenticate
from rest_framework import serializers

from apps.catalog.serializers import ProductListSerializer

from .models import Customer, Favourite


class CustomerRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=100, required=False, default="")
    last_name = serializers.CharField(max_length=100, required=False, default="")
    phone = serializers.CharField(max_length=30, required=False, default="")

    def validate_email(self, value):
        if Customer.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value.lower()

    def create(self, validated_data):
        return Customer.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone=validated_data.get("phone", ""),
        )


class CustomerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["email"], password=data["password"])
        if not user or not user.is_active:
            raise serializers.ValidationError("Invalid email or password.")
        data["customer"] = user
        return data


class CustomerProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "email", "first_name", "last_name", "phone", "full_name", "date_joined"]
        read_only_fields = ["id", "email", "date_joined", "full_name"]


class FavouriteSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = Favourite
        fields = ["id", "product", "added_at"]
        read_only_fields = ["id", "added_at"]
