from django.contrib import admin
from .models import Booking, GuestProfile, HotelProfile, Room, RoomType

admin.site.register(HotelProfile)
admin.site.register(RoomType)
admin.site.register(Room)
admin.site.register(GuestProfile)
admin.site.register(Booking)
