from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Booking, GuestProfile, HotelProfile, Room


@api_view(["GET"])
@permission_classes([AllowAny])
def hotel_detail(request):
    hotel = HotelProfile.objects.first()
    if not hotel:
        return Response({"detail": "Hotel profile not configured."}, status=404)
    return Response({
        "name": hotel.name,
        "tagline": hotel.tagline,
        "about": hotel.about,
        "phone": hotel.phone,
        "email": hotel.email,
        "address": hotel.address,
        "check_in_time": hotel.check_in_time,
        "check_out_time": hotel.check_out_time,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def room_list(request):
    rooms = Room.objects.select_related("room_type").order_by("number")
    return Response([{
        "id": room.id,
        "number": room.number,
        "floor": room.floor,
        "status": room.status,
        "type": room.room_type.name,
        "capacity": room.room_type.capacity,
        "nightly_rate": str(room.room_type.nightly_rate),
        "amenities": room.room_type.amenities,
    } for room in rooms])


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def booking_list_create(request):
    guest = GuestProfile.objects.get(user=request.user)

    if request.method == "GET":
        bookings = guest.bookings.select_related("room", "room__room_type").order_by("-created_at")
        return Response([{
            "id": b.id,
            "room": b.room.number,
            "room_type": b.room.room_type.name,
            "check_in": b.check_in,
            "check_out": b.check_out,
            "guests": b.guests,
            "status": b.status,
            "total": str(b.total_amount),
        } for b in bookings])

    data = request.data
    room = Room.objects.select_related("room_type").get(pk=data.get("room"))
    check_in = data.get("check_in")
    check_out = data.get("check_out")

    conflict = Booking.objects.filter(
        room=room,
        check_in__lt=check_out,
        check_out__gt=check_in,
    ).exclude(status="cancelled").exists()

    if conflict:
        return Response({"detail": "Room is already booked for those dates."}, status=409)

    with transaction.atomic():
        booking = Booking.objects.create(
            guest=guest,
            room=room,
            check_in=check_in,
            check_out=check_out,
            guests=int(data.get("guests", 1)),
            status="confirmed",
            special_requests=data.get("special_requests", ""),
        )

    return Response({
        "id": booking.id,
        "status": booking.status,
        "total": str(booking.total_amount),
    }, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def guest_list(request):
    guests = GuestProfile.objects.select_related("user").annotate(booking_count=__import__("django.db.models", fromlist=["Count"]).Count("bookings"))
    return Response([{
        "id": guest.id,
        "name": guest.user.get_full_name() or guest.user.email,
        "email": guest.user.email,
        "phone": guest.phone,
        "country": guest.country,
        "booking_count": guest.booking_count,
    } for guest in guests])


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def profile_detail(request):
    guest, _ = GuestProfile.objects.get_or_create(user=request.user)

    if request.method == "GET":
        return Response({
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "phone": guest.phone,
            "country": guest.country,
            "notes": guest.notes,
            "marketing_opt_in": guest.marketing_opt_in,
            "booking_count": guest.bookings.count(),
        })

    data = request.data
    user = request.user
    current_password = data.get("password")
    if not current_password or not user.check_password(str(current_password)):
        return Response(
            {"detail": "A valid current password is required to update your profile."},
            status=status.HTTP_403_FORBIDDEN,
        )

    user = request.user
    if "first_name" in data:
        user.first_name = str(data["first_name"]).strip()
    if "last_name" in data:
        user.last_name = str(data["last_name"]).strip()
    if "email" in data:
        new_email = str(data["email"]).strip().lower()
        if not new_email:
            return Response({"detail": "Email cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email__iexact=new_email).exclude(pk=user.pk).exists():
            return Response({"detail": "An account with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        user.email = new_email
        user.username = new_email
    user.save()

    if "phone" in data:
        guest.phone = str(data["phone"]).strip()
    if "country" in data:
        guest.country = str(data["country"]).strip()
    if "notes" in data:
        guest.notes = str(data["notes"]).strip()
    if "marketing_opt_in" in data:
        guest.marketing_opt_in = bool(data["marketing_opt_in"])
    guest.save()

    return Response({
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": guest.phone,
        "country": guest.country,
        "notes": guest.notes,
        "marketing_opt_in": guest.marketing_opt_in,
        "booking_count": guest.bookings.count(),
    })
