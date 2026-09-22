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


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=80, required=True)
    last_name = forms.CharField(max_length=80, required=False)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=40, required=False)
    country = forms.CharField(max_length=80, required=False)
    marketing_opt_in = forms.BooleanField(required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), required=False)

    def __init__(self, *args, user=None, profile=None, **kwargs):
        self.user = user
        self.profile = profile
        if user and profile and "initial" not in kwargs:
            kwargs["initial"] = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone": profile.phone,
                "country": profile.country,
                "marketing_opt_in": profile.marketing_opt_in,
                "notes": profile.notes,
            }
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        if self.user and User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def save(self):
        self.user.first_name = self.cleaned_data["first_name"].strip()
        self.user.last_name = self.cleaned_data["last_name"].strip()
        email = self.cleaned_data["email"].strip().lower()
        self.user.email = email
        self.user.username = email
        self.user.save()

        if self.profile:
            self.profile.phone = self.cleaned_data.get("phone", "").strip()
            self.profile.country = self.cleaned_data.get("country", "").strip()
            self.profile.marketing_opt_in = self.cleaned_data.get("marketing_opt_in", False)
            self.profile.notes = self.cleaned_data.get("notes", "").strip()
            self.profile.save()
        return self.user, self.profile
