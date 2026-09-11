from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="HotelProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("tagline", models.CharField(blank=True, max_length=240)),
                ("about", models.TextField(blank=True)),
                ("phone", models.CharField(blank=True, max_length=80)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("address", models.CharField(blank=True, max_length=240)),
                ("check_in_time", models.TimeField(default="14:00")),
                ("check_out_time", models.TimeField(default="11:00")),
            ],
        ),
        migrations.CreateModel(
            name="RoomType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("capacity", models.PositiveIntegerField(default=2)),
                ("nightly_rate", models.DecimalField(decimal_places=2, max_digits=10)),
                ("amenities", models.JSONField(blank=True, default=list)),
            ],
        ),
        migrations.CreateModel(
            name="GuestProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone", models.CharField(blank=True, max_length=40)),
                ("country", models.CharField(blank=True, max_length=80)),
                ("notes", models.TextField(blank=True)),
                ("marketing_opt_in", models.BooleanField(default=False)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Room",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.CharField(max_length=20, unique=True)),
                ("floor", models.PositiveIntegerField(default=1)),
                ("status", models.CharField(choices=[("available", "Available"), ("occupied", "Occupied"), ("cleaning", "Cleaning"), ("maintenance", "Maintenance")], default="available", max_length=20)),
                ("room_type", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="rooms", to="hotel.roomtype")),
            ],
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("check_in", models.DateField()),
                ("check_out", models.DateField()),
                ("guests", models.PositiveIntegerField(default=1)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("confirmed", "Confirmed"), ("checked_in", "Checked in"), ("checked_out", "Checked out"), ("cancelled", "Cancelled")], default="pending", max_length=20)),
                ("special_requests", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("guest", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bookings", to="hotel.guestprofile")),
                ("room", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bookings", to="hotel.room")),
            ],
        ),
    ]
