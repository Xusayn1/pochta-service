import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.locations.models import District, Region
from apps.users.models import UserAddress


PHONE_REGEX = re.compile(r"^\+998\d{9}$")
User = get_user_model()


class OTPSendSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=13)

    def validate_phone(self, value):
        if not PHONE_REGEX.match(value):
            raise serializers.ValidationError("Phone number must be in Uzbekistan format: +998XXXXXXXXX.")
        return value


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "phone", "full_name", "email", "password"]
        read_only_fields = ["id"]

    def validate_phone(self, value):
        if not PHONE_REGEX.match(value):
            raise serializers.ValidationError("Phone number must be in Uzbekistan format: +998XXXXXXXXX.")
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.username = validated_data["phone"]
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=13)
    otp = serializers.CharField(max_length=6)

    def validate_phone(self, value):
        if not PHONE_REGEX.match(value):
            raise serializers.ValidationError("Phone number must be in Uzbekistan format: +998XXXXXXXXX.")
        return value

    def validate_otp(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("OTP must be a 6-digit code.")
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "phone",
            "full_name",
            "email",
            "is_active",
            "is_staff",
            "date_joined",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "username", "is_active", "is_staff", "date_joined", "created_at", "updated_at"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["full_name", "email"]


class UserAddressSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source="region.name", read_only=True)
    district_name = serializers.CharField(source="district.name", read_only=True)
    region = serializers.PrimaryKeyRelatedField(queryset=Region.objects.filter(is_active=True))
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.filter(is_active=True))

    class Meta:
        model = UserAddress
        fields = [
            "id",
            "title",
            "region",
            "region_name",
            "district",
            "district_name",
            "address",
            "landmark",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        region = attrs.get("region", getattr(self.instance, "region", None))
        district = attrs.get("district", getattr(self.instance, "district", None))

        if region and district and district.region_id != region.id:
            raise serializers.ValidationError({"district": "Selected district does not belong to the selected region."})

        return attrs
