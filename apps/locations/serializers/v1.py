from rest_framework import serializers

from apps.locations.models import City, Region


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ["id", "name_uz", "name_ru", "name_en", "code", "delivery_days_min", "delivery_days_max", "is_active"]


class CitySerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source="region.name_en", read_only=True)

    class Meta:
        model = City
        fields = ["id", "region", "region_name", "name_uz", "name_ru", "name_en", "is_hub", "is_active"]
