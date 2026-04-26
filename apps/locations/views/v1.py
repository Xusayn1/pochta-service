from rest_framework import generics

from apps.locations.models import City, Region
from apps.locations.serializers.v1 import CitySerializer, RegionSerializer


class RegionListView(generics.ListAPIView):
    """List all active regions (public)"""
    queryset = Region.objects.filter(is_active=True)
    serializer_class = RegionSerializer
    permission_classes = []  # Allow any


class CityListView(generics.ListAPIView):
    """List cities, optionally filtered by region (public)"""
    serializer_class = CitySerializer
    permission_classes = []  # Allow any

    def get_queryset(self):
        queryset = City.objects.filter(is_active=True).select_related('region')
        region_id = self.request.query_params.get('region')
        if region_id:
            queryset = queryset.filter(region_id=region_id)
        return queryset
