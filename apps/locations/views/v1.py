from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.locations.models import Branch, District, Region
from .serializers import BranchSerializer, DistrictSerializer, RegionSerializer


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.filter(is_active=True)
    serializer_class = RegionSerializer

    @action(detail=True, methods=["get"])
    def districts(self, request, pk=None):
        districts = District.objects.filter(region=self.get_object(), is_active=True)
        serializer = DistrictSerializer(
            districts,
            many=True,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data)


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = District.objects.filter(is_active=True).select_related("region")
    serializer_class = DistrictSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        region_id = self.request.query_params.get("region")
        if region_id:
            queryset = queryset.filter(region_id=region_id)
        return queryset


class BranchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Branch.objects.filter(is_active=True).select_related("region", "district")
    serializer_class = BranchSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        region_id = self.request.query_params.get("region")
        district_id = self.request.query_params.get("district")
        branch_type = self.request.query_params.get("branch_type")

        if region_id:
            queryset = queryset.filter(region_id=region_id)
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        if branch_type:
            queryset = queryset.filter(branch_type=branch_type)
        return queryset
