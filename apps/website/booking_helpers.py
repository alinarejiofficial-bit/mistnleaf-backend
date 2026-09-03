from __future__ import annotations

from datetime import date, datetime
from urllib.parse import urlencode

from django.http import QueryDict

from apps.availability.services import get_availability
from apps.website.cms_loader import get_cms_room, get_cms_rooms


def parse_booking_query(params: QueryDict | dict) -> dict:
    getter = params.get if hasattr(params, "get") else lambda k, d="": params.get(k, d)

    def val(key: str, default: str = "") -> str:
        value = getter(key, default)
        if isinstance(value, list):
            return value[0] if value else default
        return value or default

    return {
        "check_in": val("checkIn") or val("check_in"),
        "check_out": val("checkOut") or val("check_out"),
        "guests": val("guests", "2"),
        "room": val("room"),
        "addons": val("addons"),
        "name": val("name"),
        "email": val("email"),
        "phone": val("phone"),
        "notes": val("notes"),
        "ref": val("ref"),
        "id": val("id"),
    }


def booking_query_string(data: dict, extra: dict | None = None) -> str:
    payload = {}
    mapping = {
        "check_in": "checkIn",
        "check_out": "checkOut",
        "guests": "guests",
        "room": "room",
        "addons": "addons",
        "name": "name",
        "email": "email",
        "phone": "phone",
        "notes": "notes",
        "ref": "ref",
        "id": "id",
    }
    for src, dest in mapping.items():
        value = (extra or {}).get(src, data.get(src))
        if value:
            payload[dest] = value
    return urlencode(payload)


def nights_between(check_in: str, check_out: str) -> int:
    if not check_in or not check_out:
        return 0
    start = datetime.strptime(check_in, "%Y-%m-%d").date()
    end = datetime.strptime(check_out, "%Y-%m-%d").date()
    delta = (end - start).days
    return delta if delta > 0 else 0


def require_search(query: dict) -> bool:
    guests = int(query.get("guests") or 0)
    return bool(
        query.get("check_in")
        and query.get("check_out")
        and nights_between(query["check_in"], query["check_out"]) > 0
        and guests > 0
    )


def format_stay_range(check_in: str, check_out: str) -> str:
    if not check_in or not check_out:
        return "Dates not selected"
    start = datetime.strptime(check_in, "%Y-%m-%d")
    end = datetime.strptime(check_out, "%Y-%m-%d")
    fmt = "%d %b %Y"
    return f"{start.strftime(fmt)} → {end.strftime(fmt)}"


def get_booking_availability(check_in: str, check_out: str, guests: int) -> list[dict]:
    start = datetime.strptime(check_in, "%Y-%m-%d").date()
    end = datetime.strptime(check_out, "%Y-%m-%d").date()
    api_result = get_availability(start, end, guests)
    rooms_by_slug = {room["slug"]: room for room in get_cms_rooms()}
    items = []

    for result in api_result.get("results", []):
        room = rooms_by_slug.get(result["slug"]) or {
            "slug": result["slug"],
            "name": result.get("name", result["slug"]),
            "short": "",
            "price": int(result.get("base_rate") or 0),
            "guests": result.get("max_guests", 2),
            "image": "",
            "availability": "",
        }
        estimate = result.get("estimate")
        items.append(
            {
                "room": room,
                "available": result["available"],
                "status": result["status"],
                "estimate": estimate,
                "estimate_display": f"₹{int(estimate):,}" if estimate else None,
            }
        )
    return items


def booking_progress(current_key: str) -> list[dict]:
    """Annotate booking steps with number + status for the progress nav."""
    from apps.website.content import BOOKING_STEPS

    keys = [step["key"] for step in BOOKING_STEPS]
    try:
        current_index = keys.index(current_key)
    except ValueError:
        current_index = 0

    progress = []
    for index, step in enumerate(BOOKING_STEPS):
        if index < current_index:
            status = "done"
        elif index == current_index:
            status = "active"
        else:
            status = "upcoming"
        progress.append(
            {
                **step,
                "number": index + 1,
                "status": status,
            }
        )
    return progress
