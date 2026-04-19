from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.locations.views.v1 import BranchViewSet, DistrictViewSet, RegionViewSet

app_name = "v1"

router = DefaultRouter()
router.register("regions", RegionViewSet)
router.register("districts", DistrictViewSet)
router.register("branches", BranchViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
