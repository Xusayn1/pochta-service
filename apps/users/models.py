import re

from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models


PHONE_REGEX = re.compile(r"^\+998\d{9}$")


class User(AbstractUser):
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=13, unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    class Meta:
        db_table = "users_user"
        ordering = ["-date_joined"]

    def clean(self):
        super().clean()
        if self.phone and not PHONE_REGEX.match(self.phone):
            raise ValidationError({"phone": "Phone number must be in Uzbekistan format: +998XXXXXXXXX."})

    def save(self, *args, **kwargs):
        if not self.username and self.phone:
            self.username = self.phone
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name or self.phone or self.username


class UserAddress(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="addresses")
    title = models.CharField(max_length=100, blank=True)
    region = models.ForeignKey("locations.Region", on_delete=models.PROTECT, related_name="user_addresses")
    district = models.ForeignKey("locations.District", on_delete=models.PROTECT, related_name="user_addresses")
    address = models.TextField()
    landmark = models.CharField(max_length=255, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_user_address"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.user} - {self.address[:40]}"
