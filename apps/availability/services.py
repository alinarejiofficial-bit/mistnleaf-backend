from datetime import date, timedelta

from apps.bookings.models import Booking
from apps.rooms.models import RoomType, RoomUnit


def nights_between(check_in: date, check_out: date) -> int:
    """Billable nights. Same-day check-in/out counts as 1 night."""
    if not check_in or not check_out or check_out < check_in:
        return 0
    return max((check_out - check_in).days, 1)


def exclusive_end(check_in: date, check_out: date) -> date:
    """Half-open stay end; same-day stays occupy the check-in date."""
    if check_out > check_in:
        return check_out
    return check_in + timedelta(days=1)


def dates_overlap(
    a_start: date,
    a_end: date,
    b_start: date,
    b_end: date,
) -> bool:
    a_ex = exclusive_end(a_start, a_end)
    b_ex = exclusive_end(b_start, b_end)
    return a_start < b_ex and b_start < a_ex


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
            "message": "Check-out cannot be before check-in.",
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
