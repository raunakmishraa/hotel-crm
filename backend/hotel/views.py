from datetime import date
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm, ProfileForm, SignupForm
from .models import Booking, GuestProfile, HotelProfile, Room


def hotel_context():
    return {"hotel": HotelProfile.objects.first()}


def home(request):
    return render(request, "hotel/home.html", hotel_context())


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account is ready. You can now book a room.")
        return redirect("rooms")
    return render(request, "hotel/auth.html", {
        **hotel_context(),
        "form": form,
        "mode": "signup",
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    error = None
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get("next") or "home")
        error = "Email or password is incorrect."
    return render(request, "hotel/auth.html", {
        **hotel_context(),
        "mode": "login",
        "error": error,
    })


def logout_view(request):
    logout(request)
    return redirect("home")


def rooms(request):
    room_types = []
    for room_type in __import__("hotel.models", fromlist=["RoomType"]).RoomType.objects.all():
        room_types.append({
            "type": room_type,
            "rooms": room_type.rooms.filter(status="available"),
        })
    return render(request, "hotel/rooms.html", {
        **hotel_context(),
        "room_types": room_types,
        "today": date.today().isoformat(),
    })


@login_required
def booking_create(request):
    guest = get_object_or_404(GuestProfile, user=request.user)
    form = BookingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        booking = form.save(commit=False)
        booking.guest = guest
        booking.status = "confirmed"
        booking.save()
        messages.success(request, f"Booking #{booking.pk} confirmed.")
        return redirect("my_bookings")
    return render(request, "hotel/booking_form.html", {
        **hotel_context(),
        "form": form,
    })


@login_required
def my_bookings(request):
    guest = get_object_or_404(GuestProfile, user=request.user)
    bookings = guest.bookings.select_related("room", "room__room_type").order_by("-created_at")
    return render(request, "hotel/bookings.html", {
        **hotel_context(),
        "bookings": bookings,
    })


@login_required
def profile_view(request):
    profile, _ = GuestProfile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, user=request.user, profile=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your profile details have been updated.")
        return redirect("profile")

    bookings = profile.bookings.select_related("room", "room__room_type").order_by("-created_at")
    return render(request, "hotel/profile.html", {
        **hotel_context(),
        "form": form,
        "profile": profile,
        "bookings": bookings,
        "booking_count": bookings.count(),
    })


def staff_check(user):
    return user.is_staff


@user_passes_test(staff_check, login_url="/login/")
def crm_dashboard(request):
    bookings = Booking.objects.select_related("guest__user", "room", "room__room_type").order_by("-created_at")
    context = {
        **hotel_context(),
        "bookings": bookings[:12],
        "rooms": Room.objects.select_related("room_type").order_by("number"),
        "guest_count": GuestProfile.objects.count(),
        "booking_count": Booking.objects.exclude(status="cancelled").count(),
        "confirmed_count": Booking.objects.filter(status="confirmed").count(),
        "revenue": Booking.objects.exclude(status="cancelled").aggregate(total=Sum("room__room_type__nightly_rate"))["total"] or 0,
    }
    return render(request, "crm/dashboard.html", context)
