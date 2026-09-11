from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("hotel.urls")),
    path("api/v1/", include("hotel.api_urls")),
]
