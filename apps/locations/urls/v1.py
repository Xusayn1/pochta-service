from django.urls import path

from apps.locations.views.v1 import CityListView, RegionListView

app_name = "v1"

urlpatterns = [
    path("regions/", RegionListView.as_view(), name="region-list"),
    path("cities/", CityListView.as_view(), name="city-list"),
]
