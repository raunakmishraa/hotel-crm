from django.urls import path
from . import api_views

urlpatterns = [
    path("hotel/", api_views.hotel_detail),
    path("rooms/", api_views.room_list),
    path("bookings/", api_views.booking_list_create),
    path("guests/", api_views.guest_list),
]
