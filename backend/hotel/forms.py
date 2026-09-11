from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking, GuestProfile


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=80)
    last_name = forms.CharField(max_length=80, required=False)
    phone = forms.CharField(max_length=40, required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"].lower()
        user.email = self.cleaned_data["email"].lower()
        if commit:
            user.save()
            GuestProfile.objects.create(
                user=user,
                phone=self.cleaned_data.get("phone", ""),
            )
        return user


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ("room", "check_in", "check_out", "guests", "special_requests")
        widgets = {
            "check_in": forms.DateInput(attrs={"type": "date"}),
            "check_out": forms.DateInput(attrs={"type": "date"}),
            "special_requests": forms.Textarea(attrs={"rows": 4}),
        }

    def clean(self):
        cleaned = super().clean()
        room = cleaned.get("room")
        check_in = cleaned.get("check_in")
        check_out = cleaned.get("check_out")
        guests = cleaned.get("guests")

        if check_in and check_out and check_out <= check_in:
            raise forms.ValidationError("Check-out must be after check-in.")

        if room and room.status in {"maintenance", "cleaning"}:
            raise forms.ValidationError("This room is not currently bookable.")

        if room and guests and guests > room.room_type.capacity:
            raise forms.ValidationError("Guest count exceeds this room's capacity.")

        if room and check_in and check_out:
            conflict = Booking.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in,
            ).exclude(status="cancelled").exists()
            if conflict:
                raise forms.ValidationError("That room is already booked for those dates.")

        return cleaned
