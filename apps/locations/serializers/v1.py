from rest_framework import serializers
from apps.locations.models import Branch, District, Region


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ["id", "name", "name_uz", "name_ru", "code", "is_active"]


class DistrictSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source="region.name", read_only=True)

    class Meta:
        model = District
        fields = ["id", "region", "region_name", "name", "name_uz", "name_ru", "code", "is_active"]


class BranchSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source="region.name", read_only=True)
    district_name = serializers.CharField(source="district.name", read_only=True)

    class Meta:
        model = Branch
        fields = [
            "id",
            "name",
            "branch_type",
            "region",
            "region_name",
            "district",
            "district_name",
            "address",
            "latitude",
            "longitude",
            "phone",
            "working_hours",
            "is_active",
        ]
