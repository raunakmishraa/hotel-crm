from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("rooms/", views.rooms, name="rooms"),
    path("book/", views.booking_create, name="booking_create"),
    path("bookings/", views.my_bookings, name="my_bookings"),
    path("profile/", views.profile_view, name="profile"),
    path("crm/", views.crm_dashboard, name="crm_dashboard"),
]
