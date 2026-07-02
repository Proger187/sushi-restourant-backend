from django.contrib.auth.models import User
from rest_framework import serializers


class CustomerRegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=30)
    name = serializers.CharField(max_length=100)
    password = serializers.CharField(min_length=6, write_only=True)

    def validate_phone(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["phone"],
            first_name=validated_data["name"],
            password=validated_data["password"],
        )


class CustomerProfileSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="username", read_only=True)
    name = serializers.CharField(source="first_name")

    class Meta:
        model = User
        fields = ["id", "phone", "name"]
        read_only_fields = ["id", "phone"]
