from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from hotel.models import Booking, GuestProfile, HotelProfile, Room, RoomType
import json
from pathlib import Path


class Command(BaseCommand):
    help = "Load the hotel demo data and demo users."

    def handle(self, *args, **options):
        fixture = Path(__file__).resolve().parents[2] / "fixtures" / "hotel_data.json"
        data = json.loads(fixture.read_text(encoding="utf-8"))

        HotelProfile.objects.update_or_create(
            pk=1,
            defaults=data["hotel"],
        )

        for item in data["room_types"]:
            RoomType.objects.update_or_create(
                name=item["name"],
                defaults={
                    "description": item["description"],
                    "capacity": item["capacity"],
                    "nightly_rate": Decimal(str(item["nightly_rate"])),
                    "amenities": item["amenities"],
                },
            )

        room_map = {rt.name: rt for rt in RoomType.objects.all()}
        for item in data["rooms"]:
            Room.objects.update_or_create(
                number=item["number"],
                defaults={
                    "floor": item["floor"],
                    "room_type": room_map[item["room_type"]],
                    "status": item["status"],
                },
            )

        admin, _ = User.objects.get_or_create(
            username="admin@harborhouse.test",
            defaults={
                "email": "admin@harborhouse.test",
                "first_name": "Maya",
                "last_name": "Shrestha",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("Admin123!")
        admin.save()

        guest_user, _ = User.objects.get_or_create(
            username="guest@example.com",
            defaults={
                "email": "guest@example.com",
                "first_name": "Arun",
                "last_name": "Karki",
            },
        )
        guest_user.set_password("Guest123!")
        guest_user.save()
        guest, _ = GuestProfile.objects.get_or_create(
            user=guest_user,
            defaults={"phone": "+977 9800000000", "country": "Nepal"},
        )

        room = Room.objects.filter(status="available").first()
        if room and not Booking.objects.filter(guest=guest).exists():
            Booking.objects.create(
                guest=guest,
                room=room,
                check_in=date.today() + timedelta(days=5),
                check_out=date.today() + timedelta(days=7),
                guests=2,
                status="confirmed",
                special_requests="Late arrival around 8 PM.",
            )

        self.stdout.write(self.style.SUCCESS("Demo hotel data and accounts are ready."))
