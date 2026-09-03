"""Website-side helpers for persisting enquiries and bookings."""
from __future__ import annotations

from apps.bookings.models import Booking
from apps.enquiries.models import Enquiry


def create_website_enquiry(*, name: str, email: str, phone: str, subject: str, message: str) -> Enquiry:
    return Enquiry.objects.create(
        name=name.strip(),
        email=email.strip(),
        phone=phone.strip(),
        subject=subject.strip(),
        message=message.strip(),
        channel=Enquiry.Channel.WEBSITE,
        status=Enquiry.Status.NEW,
    )


def create_website_booking(
    *,
    guest_name: str,
    guest_email: str,
    guest_phone: str,
    room_type,
    check_in,
    check_out,
    adults: int,
    children: int,
    amount,
    notes: str = "",
) -> Booking:
    return Booking.objects.create(
        guest_name=guest_name.strip(),
        guest_email=guest_email.strip(),
        guest_phone=guest_phone.strip(),
        room_type=room_type,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        children=children,
        amount=amount,
        notes=notes,
        status=Booking.Status.PENDING,
        payment_status=Booking.PaymentStatus.PENDING,
        source=Booking.Source.DIRECT_WEBSITE,
    )
