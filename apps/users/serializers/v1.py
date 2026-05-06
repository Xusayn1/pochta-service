from uuid import uuid4

from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.users.models import PHONE_REGEX, UserAddress

User = get_user_model()



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)
    phone = serializers.CharField(required=False, allow_blank=True)

    role = serializers.ChoiceField(
        choices=[
            User.Roles.USER,
            User.Roles.COURIER,
            User.Roles.MANAGER,
        ],
        default=User.Roles.USER,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "full_name",
            "email",
            "phone",
            "password",
            "confirm_password",
            "role",
        ]

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        return attrs

    def validate_phone(self, value):
        if value:
            if not PHONE_REGEX.match(value):
                raise serializers.ValidationError(
                    "Phone number must be in Uzbekistan format: +998XXXXXXXXX."
                )

            if User.objects.filter(phone=value).exists():
                raise serializers.ValidationError(
                    "A user with this phone number already exists."
                )

        return value

    def validate_username(self, value):
        if value and User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )

        return value

    def validate_email(self, value):
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        password = validated_data.pop("password")

        username = validated_data.get("username")
        email = validated_data.get("email")
        phone = validated_data.get("phone")

        # username auto generate
        if not username and email:
            username = email.split("@")[0]

        if not username:
            username = f"user_{uuid4().hex[:8]}"

        # phone auto generate
        if not phone:
            for _ in range(10):
                generated_phone = f"+998{uuid4().int % 1_000_000_000:09d}"

                if not User.objects.filter(phone=generated_phone).exists():
                    phone = generated_phone
                    break

        validated_data["username"] = username
        validated_data["phone"] = phone

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

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

    def validate(self, attrs):
        identifier = attrs.get('identifier') or attrs.get('username') or attrs.get('email') or attrs.get('phone')
        password = attrs.get('password')

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

        attrs["user"] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "phone",
            "full_name",
            "email",
            "role",
            "is_verified",
            "created_at",
        ]
        read_only_fields = ["id", "username", "phone", "role", "is_verified", "created_at"]


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = [
            "id",
            "title",
            "full_address",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        # User is passed by perform_create in the view
        user = validated_data.pop("user", None) or self.context.get("request").user # type: ignore[index]
        make_default = validated_data.get("is_default", False)
        
        # If no other addresses exist or this is marked as default, make it default
        if make_default or not UserAddress.objects.filter(user=user).exists(): # type: ignore[attr-defined]
            # Clear default flag on other addresses
            UserAddress.objects.filter(user=user, is_default=True).update(is_default=False) # type: ignore[attr-defined]
            validated_data["is_default"] = True
        else:
            validated_data["is_default"] = False
        
        return UserAddress.objects.create(user=user, **validated_data) # type: ignore[attr-defined]

    def update(self, instance, validated_data):
        user = instance.user
        make_default = validated_data.get("is_default", instance.is_default)
        
        if make_default and not instance.is_default:
            # Clear default flag on other addresses
            UserAddress.objects.filter(user=user, is_default=True).update(is_default=False) # type: ignore[attr-defined]
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

