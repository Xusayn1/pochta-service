import re
from uuid import uuid4

from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.users.models import UserAddress

PHONE_REGEX = re.compile(r"^\+998\d{9}$")
User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6, required=False)
    username = serializers.CharField(required=False)
    phone = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(
        choices=[User.Roles.USER, User.Roles.COURIER, User.Roles.MANAGER, "customer"],
        default=User.Roles.USER,
        required=False,
    )

    class Meta:
        model = User
        fields = ["username", "phone", "full_name", "email", "password", "confirm_password", "role"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if confirm_password is not None and password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        role = attrs.get("role", User.Roles.USER)
        if role == "customer":
            attrs["role"] = User.Roles.USER

        return attrs

    def validate_phone(self, value):
        if not PHONE_REGEX.match(value):
            raise serializers.ValidationError("Phone number must be in Uzbekistan format: +998XXXXXXXXX.")
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("confirm_password", None)

        username = validated_data.pop("username", None)
        email = validated_data.get("email")
        phone = validated_data.get("phone")

        if not username and email:
            username = email.split("@")[0]
        if not username:
            raise serializers.ValidationError({"username": "Username is required."})

        if not phone:
            for _ in range(10):
                generated_phone = f"+998{uuid4().int % 1_000_000_000:09d}"
                if not User.objects.filter(phone=generated_phone).exists():
                    phone = generated_phone
                    break
            if not phone:
                raise serializers.ValidationError({"phone": "Unable to generate a unique phone number."})

        validated_data["phone"] = phone
        validated_data["username"] = username
        validated_data["role"] = User.normalize_role(validated_data.get("role", User.Roles.USER))
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=13, required=False)
    password = serializers.CharField(write_only=True)

    def validate_phone(self, value):
        if not PHONE_REGEX.match(value):
            raise serializers.ValidationError("Phone number must be in Uzbekistan format: +998XXXXXXXXX.")
        return value

    def validate(self, data):
        identifier = data.get('identifier') or data.get('username') or data.get('email') or data.get('phone')
        password = data.get('password')

        if not identifier:
            raise serializers.ValidationError("Username, email, or phone is required.")

        user = User.objects.filter(username=identifier).first()
        if not user:
            user = User.objects.filter(email__iexact=identifier).first()
        if not user:
            user = User.objects.filter(phone=identifier).first()
        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials.")

        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone", "full_name", "email", "role", "is_verified", "created_at"]
        read_only_fields = ["id", "phone", "role", "is_verified", "created_at"]


class UserAddressSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source="region.name_en", read_only=True)
    city_name = serializers.CharField(source="city.name_en", read_only=True)
    full_address = serializers.SerializerMethodField()

    class Meta:
        model = UserAddress
        fields = [
            "id",
            "user",
            "title",
            "region",
            "region_name",
            "city",
            "city_name",
            "address",
            "landmark",
            "is_default",
            "full_address",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "region_name",
            "city_name",
            "full_address",
            "created_at",
            "updated_at",
        ]

    def get_full_address(self, obj):
        parts = [obj.title, obj.city.name_en, obj.address, obj.landmark]
        return ", ".join(part for part in parts if part)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        region = attrs.get("region") or getattr(self.instance, "region", None)
        city = attrs.get("city") or getattr(self.instance, "city", None)

        if region and city and city.region_id != region.id:
            raise serializers.ValidationError({
                "city": "Selected city does not belong to the selected region."
            })

        return attrs

    def _sync_default_flag(self, user, make_default, current_instance=None):
        if make_default:
            queryset = UserAddress.objects.filter(user=user, is_default=True)
            if current_instance is not None:
                queryset = queryset.exclude(pk=current_instance.pk)
            queryset.update(is_default=False)
        elif not UserAddress.objects.filter(user=user).exclude(
            pk=getattr(current_instance, "pk", None)
        ).exists():
            return True

        return make_default

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        validated_data["is_default"] = self._sync_default_flag(
            user=user,
            make_default=validated_data.get("is_default", False),
        )
        return UserAddress.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        user = instance.user
        validated_data["is_default"] = self._sync_default_flag(
            user=user,
            make_default=validated_data.get("is_default", instance.is_default),
            current_instance=instance,
        )
        return super().update(instance, validated_data)
