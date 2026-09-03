from django.contrib import admin

from .models import Enquiry


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("reference", "name", "email", "subject", "channel", "status", "received_at")
    list_filter = ("status", "channel")
    search_fields = ("reference", "name", "email", "subject")
    readonly_fields = ("reference", "received_at", "updated_at")
