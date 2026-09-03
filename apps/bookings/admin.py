from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "guest_name",
        "room_type",
        "room_unit",
        "check_in",
        "check_out",
        "status",
        "payment_status",
    )
    list_filter = ("status", "payment_status", "source", "room_type")
    search_fields = ("reference", "guest_name", "guest_email")
