from datetime import date

from apps.bookings.models import Booking
from apps.rooms.models import RoomType, RoomUnit


def nights_between(check_in: date, check_out: date) -> int:
    if not check_in or not check_out:
        return 0
    delta = (check_out - check_in).days
    return delta if delta > 0 else 0


def dates_overlap(
    a_start: date,
    a_end: date,
    b_start: date,
    b_end: date,
) -> bool:
    return a_start < b_end and b_start < a_end


def is_unit_available(
    unit: RoomUnit,
    check_in: date,
    check_out: date,
    ignore_booking_id=None,
) -> bool:
    if unit.status == RoomUnit.Status.MAINTENANCE or not unit.is_active:
        return False

    blocking = Booking.objects.filter(
        room_unit=unit,
        status__in=Booking.blocking_statuses(),
    )
    if ignore_booking_id:
        blocking = blocking.exclude(id=ignore_booking_id)

    for booking in blocking:
        if dates_overlap(check_in, check_out, booking.check_in, booking.check_out):
            return False
    return True


def available_units_for_type(
    room_type: RoomType,
    check_in: date,
    check_out: date,
    ignore_booking_id=None,
) -> list[RoomUnit]:
    units = room_type.units.filter(is_active=True)
    return [
        unit
        for unit in units
        if is_unit_available(unit, check_in, check_out, ignore_booking_id)
    ]


def check_room_type_availability(
    room_type: RoomType,
    check_in: date,
    check_out: date,
    guests: int,
    nights: int,
) -> dict:
    fits = room_type.max_guests >= guests and nights > 0
    open_units = (
        available_units_for_type(room_type, check_in, check_out)
        if fits and nights > 0
        else []
    )
    units_open = len(open_units)

    if not fits:
        status = "too-small"
        available = False
    elif units_open == 0:
        status = "sold-out"
        available = False
    elif units_open == 1:
        status = "limited"
        available = True
    else:
        status = "available"
        available = True

    estimate = None
    if fits and nights > 0:
        estimate = float(room_type.base_rate) * nights

    return {
        "room_type_id": str(room_type.id),
        "slug": room_type.slug,
        "name": room_type.name,
        "max_guests": room_type.max_guests,
        "base_rate": float(room_type.base_rate),
        "available": available,
        "status": status,
        "units_available": units_open,
        "nights": nights,
        "estimate": estimate,
        "open_unit_codes": [u.code for u in open_units],
    }


def get_availability(
    check_in: date,
    check_out: date,
    guests: int = 2,
    room_type_slug: str | None = None,
) -> dict:
    nights = nights_between(check_in, check_out)
    if nights < 1:
        return {
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "guests": guests,
            "nights": 0,
            "valid": False,
            "message": "Check-out must be after check-in.",
            "results": [],
        }

    queryset = RoomType.objects.filter(is_active=True).prefetch_related("units")
    if room_type_slug:
        queryset = queryset.filter(slug=room_type_slug)

    results = [
        check_room_type_availability(room_type, check_in, check_out, guests, nights)
        for room_type in queryset
    ]

    return {
        "check_in": check_in.isoformat(),
        "check_out": check_out.isoformat(),
        "guests": guests,
        "nights": nights,
        "valid": True,
        "results": results,
        "any_available": any(r["available"] for r in results),
    }
