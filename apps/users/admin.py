from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.users.models import User, UserAddress


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'role', 'is_verified')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2'),
        }),
    )
    list_display = ('phone', 'full_name', 'role', 'is_verified', 'is_active', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('phone', 'full_name', 'email')
    ordering = ('-date_joined',)
    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'region', 'city', 'address', 'is_default', 'created_at')
    list_filter = ('region', 'city', 'is_default', 'created_at')
    search_fields = ('user__phone', 'user__full_name', 'title', 'address', 'city__name_en', 'region__name_en')
    readonly_fields = ('created_at', 'updated_at')

