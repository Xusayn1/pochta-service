
from django.contrib import admin

from apps.shared.models import Media, Onboarding, FAQ


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'file_type', 'mime_type', 'size', 'created_at')
    list_filter = ('file_type',)
    search_fields = ('original_name', 'mime_type')
    readonly_fields = ('uuid', 'original_name', 'size', 'mime_type', 'file_type', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(Onboarding)
class OnboardingAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_completed')
    list_filter = ('is_completed',)
    search_fields = ('user__username', 'user__email')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('question', 'answer')