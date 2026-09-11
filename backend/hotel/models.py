from django.conf import settings
from django.db import models


class HotelProfile(models.Model):
    name = models.CharField(max_length=160)
    tagline = models.CharField(max_length=240, blank=True)
    about = models.TextField(blank=True)
    phone = models.CharField(max_length=80, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=240, blank=True)
    check_in_time = models.TimeField(default="14:00")
    check_out_time = models.TimeField(default="11:00")

    def __str__(self):
        return self.name


class RoomType(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(default=2)
    nightly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    amenities = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("occupied", "Occupied"),
        ("cleaning", "Cleaning"),
        ("maintenance", "Maintenance"),
    ]
    number = models.CharField(max_length=20, unique=True)
    floor = models.PositiveIntegerField(default=1)
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT, related_name="rooms")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")

    def __str__(self):
        return f"{self.number} · {self.room_type.name}"


class GuestProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=40, blank=True)
    country = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)
    marketing_opt_in = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("checked_in", "Checked in"),
        ("checked_out", "Checked out"),
        ("cancelled", "Cancelled"),
    ]
    guest = models.ForeignKey(GuestProfile, on_delete=models.PROTECT, related_name="bookings")
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="bookings")
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def nights(self):
        return max((self.check_out - self.check_in).days, 0)

    @property
    def total_amount(self):
        return self.nights * self.room.room_type.nightly_rate

    def __str__(self):
        return f"Booking #{self.pk} · Room {self.room.number}"
