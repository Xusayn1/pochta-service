from django.contrib import admin
from .models import Region, City

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_uz', 'name_ru', 'name_en')
    search_fields = ('name_uz', 'name_ru', 'name_en')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_uz', 'name_ru', 'name_en', 'region')
    search_fields = ('name_uz', 'name_ru', 'name_en')
    list_filter = ('region',)
