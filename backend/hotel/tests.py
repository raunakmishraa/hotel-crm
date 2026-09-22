from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from hotel.models import Booking, GuestProfile, HotelProfile, Room, RoomType


class ProfileTests(TestCase):
    def setUp(self):
        self.hotel = HotelProfile.objects.create(
            name="Harbor House",
            tagline="Coastal sanctuary",
            email="stay@harborhouse.test",
        )
        self.user = User.objects.create_user(
            username="guest@example.com",
            email="guest@example.com",
            password="Password123!",
            first_name="Arun",
            last_name="Karki",
        )
        self.profile = GuestProfile.objects.create(
            user=self.user,
            phone="+977 9800000000",
            country="Nepal",
            notes="Quiet room preferred",
            marketing_opt_in=False,
        )
        self.other_user = User.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="Password123!",
            first_name="Other",
            last_name="User",
        )
        self.client = Client()

    def test_profile_requires_login(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_profile_renders_for_authenticated_guest(self):
        self.client.login(username="guest@example.com", password="Password123!")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hotel/profile.html")
        self.assertContains(response, "Arun Karki")
        self.assertContains(response, "guest@example.com")
        self.assertContains(response, "+977 9800000000")
        self.assertContains(response, "Nepal")
        self.assertContains(response, "Quiet room preferred")

    def test_profile_is_read_only_until_edit_is_selected(self):
        self.client.login(username="guest@example.com", password="Password123!")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit profile")
        self.assertNotContains(response, "Confirm your current password")

        edit_response = self.client.get(reverse("profile_edit"))
        self.assertEqual(edit_response.status_code, 200)
        self.assertTemplateUsed(edit_response, "hotel/profile_edit.html")
        self.assertContains(edit_response, "Confirm your current password")

    def test_profile_update_requires_current_password(self):
        self.client.login(username="guest@example.com", password="Password123!")
        response = self.client.post(reverse("profile_edit"), {
            "first_name": "Changed",
            "last_name": "Name",
            "email": "changed@example.com",
            "phone": "+977 9811111111",
            "country": "Canada",
            "notes": "Changed notes",
            "password": "WrongPassword!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter your current password to save profile changes.")

        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.first_name, "Arun")
        self.assertEqual(self.user.email, "guest@example.com")
        self.assertEqual(self.profile.country, "Nepal")

    def test_profile_update_successful(self):
        self.client.login(username="guest@example.com", password="Password123!")
        response = self.client.post(reverse("profile_edit"), {
            "first_name": "Arun Kumar",
            "last_name": "Karki Updated",
            "email": "guest.updated@example.com",
            "phone": "+977 9811111111",
            "country": "Switzerland",
            "notes": "High floor with ocean view",
            "marketing_opt_in": "on",
            "password": "Password123!",
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your profile details have been updated.")

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.first_name, "Arun Kumar")
        self.assertEqual(self.user.last_name, "Karki Updated")
        self.assertEqual(self.user.email, "guest.updated@example.com")
        self.assertEqual(self.user.username, "guest.updated@example.com")
        self.assertEqual(self.profile.phone, "+977 9811111111")
        self.assertEqual(self.profile.country, "Switzerland")
        self.assertEqual(self.profile.notes, "High floor with ocean view")
        self.assertTrue(self.profile.marketing_opt_in)

    def test_profile_duplicate_email_rejected(self):
        self.client.login(username="guest@example.com", password="Password123!")
        response = self.client.post(reverse("profile_edit"), {
            "first_name": "Arun",
            "last_name": "Karki",
            "email": "other@example.com",  # Already taken
            "phone": "+977 9800000000",
            "country": "Nepal",
            "notes": "",
            "password": "Password123!",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "An account with this email address already exists.")

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "guest@example.com")

    def test_staff_user_auto_creates_profile(self):
        staff = User.objects.create_user(
            username="admin@harborhouse.test",
            email="admin@harborhouse.test",
            password="AdminPassword123!",
            first_name="Maya",
            last_name="Shrestha",
            is_staff=True,
        )
        self.client.login(username="admin@harborhouse.test", password="AdminPassword123!")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Staff account")
        self.assertTrue(GuestProfile.objects.filter(user=staff).exists())

    def test_api_profile_detail_get_and_update(self):
        # Unauthenticated
        response = self.client.get("/api/v1/profile/")
        self.assertIn(response.status_code, [401, 403])

        # Authenticated GET
        self.client.login(username="guest@example.com", password="Password123!")
        response = self.client.get("/api/v1/profile/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], "Arun")
        self.assertEqual(data["email"], "guest@example.com")
        self.assertEqual(data["phone"], "+977 9800000000")

        # Authenticated PATCH requires the current password.
        response = self.client.patch(
            "/api/v1/profile/",
            data={"phone": "+1 555-0199"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

        # Authenticated PATCH
        response = self.client.patch(
            "/api/v1/profile/",
            data={
                "phone": "+1 555-0199",
                "country": "Canada",
                "marketing_opt_in": True,
                "password": "Password123!",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["phone"], "+1 555-0199")
        self.assertEqual(data["country"], "Canada")
        self.assertTrue(data["marketing_opt_in"])
