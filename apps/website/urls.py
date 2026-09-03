from django.urls import path

from . import views

app_name = "website"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("rooms/", views.rooms_list, name="rooms"),
    path("rooms/<slug:slug>/", views.room_detail, name="room_detail"),
    path("experiences/", views.experiences, name="experiences"),
    path("amenities/", views.amenities, name="amenities"),
    path("gallery/", views.gallery, name="gallery"),
    path("offers/", views.offers, name="offers"),
    path("dining/", views.dining, name="dining"),
    path("things-to-do/", views.things_to_do, name="things_to_do"),
    path("location/", views.location, name="location"),
    path("contact/", views.contact, name="contact"),
    path("faqs/", views.faqs, name="faqs"),
    path("explore/", views.explore, name="explore"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("cancellation/", views.cancellation, name="cancellation"),
    path("booking/", views.booking_entry, name="booking"),
    path("booking/search/", views.booking_search, name="booking_search"),
    path("booking/availability/", views.booking_availability, name="booking_availability"),
    path("booking/select/", views.booking_select, name="booking_select"),
    path("booking/add-ons/", views.booking_guest, name="booking_addons"),
    path("booking/guest/", views.booking_guest, name="booking_guest"),
    path("booking/summary/", views.booking_summary, name="booking_summary"),
    path("booking/payment/", views.booking_payment, name="booking_payment"),
    path("booking/confirmation/", views.booking_confirmation, name="booking_confirmation"),
]
