from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.bookings.models import Booking
from apps.bookings.serializers import sync_room_unit_from_booking
from apps.maintenance.models import MaintenanceTicket
from apps.rooms.models import RoomUnit


def _booking(
    reference,
    guest_name,
    guest_email,
    guest_phone,
    unit,
    check_in,
    check_out,
    status,
    source,
    payment_status,
    adults=2,
    children=0,
    paid_ratio=1,
    notes="",
):
    nights = max((check_out - check_in).days, 1)
    amount = unit.room_type.base_rate * nights
    paid = amount * Decimal(str(paid_ratio))
    booking, created = Booking.objects.update_or_create(
        reference=reference,
        defaults={
            "guest_name": guest_name,
            "guest_email": guest_email,
            "guest_phone": guest_phone,
            "room_type": unit.room_type,
            "room_unit": unit,
            "check_in": check_in,
            "check_out": check_out,
            "adults": adults,
            "children": children,
            "status": status,
            "source": source,
            "payment_status": payment_status,
            "amount": amount,
            "paid_amount": paid,
            "notes": notes,
        },
    )
    sync_room_unit_from_booking(booking)
    return created


class Command(BaseCommand):
    help = "Seed demo bookings and maintenance tickets for staff dashboards."

    def handle(self, *args, **options):
        today = timezone.localdate()
        units = {unit.code: unit for unit in RoomUnit.objects.select_related("room_type")}
        required = ["CS-01", "CS-02", "MC-01", "MC-02", "LR-01", "LR-02"]
        missing = [code for code in required if code not in units]
        if missing:
            self.stdout.write(self.style.ERROR(f"Missing room units {missing}. Run seed_rooms first."))
            return

        specs = [
            (
                "RSV-2041",
                "Ananya Sharma",
                "ananya.sharma@email.com",
                "+91 98765 41021",
                "CS-01",
                today,
                today + timedelta(days=3),
                Booking.Status.CONFIRMED,
                Booking.Source.DIRECT_WEBSITE,
                Booking.PaymentStatus.PAID,
                2,
                1,
                1,
                "",
            ),
            (
                "RSV-2042",
                "Rahul Mehta",
                "rahul.mehta@email.com",
                "+91 98200 11844",
                "LR-01",
                today,
                today + timedelta(days=2),
                Booking.Status.PENDING,
                Booking.Source.OTA,
                Booking.PaymentStatus.PENDING,
                2,
                0,
                0,
                "Awaiting card authorization",
            ),
            (
                "RSV-2038",
                "Priya Nair",
                "priya.nair@email.com",
                "+91 97654 22018",
                "MC-01",
                today - timedelta(days=1),
                today + timedelta(days=4),
                Booking.Status.CHECKED_IN,
                Booking.Source.TRAVEL_AGENT,
                Booking.PaymentStatus.PARTIAL,
                2,
                0,
                0.55,
                "",
            ),
            (
                "RSV-2045",
                "James Carter",
                "james.carter@email.com",
                "+1 415 882 4410",
                "CS-02",
                today + timedelta(days=1),
                today + timedelta(days=5),
                Booking.Status.CONFIRMED,
                Booking.Source.DIRECT_WEBSITE,
                Booking.PaymentStatus.PAID,
                2,
                0,
                1,
                "",
            ),
            (
                "RSV-2033",
                "Meera Iyer",
                "meera.iyer@email.com",
                "+91 99001 33455",
                "CS-03" if "CS-03" in units else "CS-02",
                today - timedelta(days=2),
                today,
                Booking.Status.CHECKED_OUT,
                Booking.Source.WALK_IN,
                Booking.PaymentStatus.PAID,
                1,
                0,
                1,
                "",
            ),
            (
                "RSV-2040",
                "Hiroshi Tanaka",
                "h.tanaka@email.com",
                "+81 90 1122 8899",
                "LR-03" if "LR-03" in units else "LR-01",
                today - timedelta(days=2),
                today,
                Booking.Status.CHECKED_IN,
                Booking.Source.OTA,
                Booking.PaymentStatus.PAID,
                2,
                0,
                1,
                "",
            ),
            (
                "RSV-2036",
                "Daniel Ortiz",
                "d.ortiz@email.com",
                "+34 612 445 778",
                "MC-03" if "MC-03" in units else "MC-01",
                today - timedelta(days=4),
                today,
                Booking.Status.CHECKED_OUT,
                Booking.Source.OTA,
                Booking.PaymentStatus.PAID,
                2,
                0,
                1,
                "",
            ),
            (
                "RSV-2046",
                "Kavya Menon",
                "kavya.m@email.com",
                "+91 98450 11990",
                "MC-02",
                today + timedelta(days=3),
                today + timedelta(days=7),
                Booking.Status.PENDING,
                Booking.Source.DIRECT_WEBSITE,
                Booking.PaymentStatus.PENDING,
                2,
                2,
                0,
                "",
            ),
            (
                "RSV-2030",
                "Arjun Desai",
                "arjun.desai@email.com",
                "+91 97222 88001",
                "LR-02",
                today - timedelta(days=6),
                today - timedelta(days=4),
                Booking.Status.CANCELLED,
                Booking.Source.WALK_IN,
                Booking.PaymentStatus.REFUNDED,
                1,
                0,
                0,
                "Guest cancelled 24h before arrival",
            ),
        ]

        created = 0
        for spec in specs:
            unit_code = spec[4]
            if unit_code not in units:
                continue
            if _booking(*spec[:4], units[unit_code], *spec[5:]):
                created += 1

        leak_unit = units.get("LR-04") or units.get("LR-02")
        tickets = [
            {
                "reference": "MT-11",
                "room_unit": leak_unit,
                "room": leak_unit.display_name if leak_unit else "Leaf Room",
                "issue": "Plumbing leak under bathroom sink",
                "category": MaintenanceTicket.Category.PLUMBING,
                "priority": MaintenanceTicket.Priority.HIGH,
                "status": MaintenanceTicket.Status.OPEN,
                "reported_by": "Housekeeping",
            },
            {
                "reference": "MT-12",
                "room_unit": units.get("MC-01"),
                "room": units["MC-01"].display_name,
                "issue": "TV remote not pairing",
                "category": MaintenanceTicket.Category.ELECTRICAL,
                "priority": MaintenanceTicket.Priority.LOW,
                "status": MaintenanceTicket.Status.RESOLVED,
                "reported_by": "Guest",
            },
            {
                "reference": "MT-13",
                "room_unit": units.get("CS-02"),
                "room": units["CS-02"].display_name,
                "issue": "AC not cooling overnight",
                "category": MaintenanceTicket.Category.HVAC,
                "priority": MaintenanceTicket.Priority.CRITICAL,
                "status": MaintenanceTicket.Status.IN_PROGRESS,
                "reported_by": "Front Desk",
            },
        ]
        ticket_created = 0
        for data in tickets:
            _, was_created = MaintenanceTicket.objects.update_or_create(
                reference=data["reference"],
                defaults=data,
            )
            if was_created:
                ticket_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Bookings created: {created}, maintenance tickets created: {ticket_created}"
            )
        )
