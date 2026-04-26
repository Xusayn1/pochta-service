import re

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models


PHONE_REGEX = re.compile(r"^\+998\d{9}$")


class CustomUserManager(BaseUserManager):
    """Custom user manager for phone-based authentication"""

    def create_user(self, phone, password=None, **extra_fields):
        """Create and save a regular user"""
        if not phone:
            raise ValueError('Phone number is required')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Roles.MANAGER)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractUser):
    class Roles(models.TextChoices):
        USER = "user", "User"
        COURIER = "courier", "Courier"
        MANAGER = "manager", "Manager"

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=13, unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.USER)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = "users_user"
        ordering = ["-date_joined"]

    LEGACY_ROLE_MAP = {
        "client": Roles.USER,
        "customer": Roles.USER,
        "admin": Roles.MANAGER,
    }

    def clean(self):
        super().clean()
        if self.phone and not PHONE_REGEX.match(self.phone):
            raise ValidationError({"phone": "Phone number must be in Uzbekistan format: +998XXXXXXXXX."})
        self.role = self.normalize_role(self.role)

    def save(self, *args, **kwargs):
        if not self.username and self.phone:
            self.username = self.phone
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name or self.phone or self.username

    @classmethod
    def normalize_role(cls, role_value):
        if not role_value:
            return cls.Roles.USER
        return cls.LEGACY_ROLE_MAP.get(role_value, role_value)

    @property
    def is_manager(self):
        role = self.normalize_role(self.role)
        return role == self.Roles.MANAGER or self.is_superuser or self.is_staff

    @property
    def is_courier(self):
        return self.normalize_role(self.role) == self.Roles.COURIER

    @property
    def is_customer(self):
        return self.normalize_role(self.role) == self.Roles.USER


class UserAddress(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="addresses")
    title = models.CharField(max_length=100, blank=True)
    region = models.ForeignKey("locations.Region", on_delete=models.PROTECT, related_name="user_addresses")
    city = models.ForeignKey("locations.City", on_delete=models.PROTECT, related_name="user_addresses")
    address = models.TextField()
    landmark = models.CharField(max_length=255, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_user_address"
        ordering = ["-is_default", "-created_at"]

    @property
    def full_address(self):
        parts = [self.title, self.city.name_en, self.address, self.landmark]
        return ", ".join(part for part in parts if part)

    def __str__(self):
        return self.full_address or f"{self.user} - {self.address[:40]}"
