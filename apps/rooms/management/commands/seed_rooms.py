from django.core.management.base import BaseCommand

from apps.rooms.models import RoomType, RoomUnit

ROOM_TYPES = [
    {
        "slug": "canopy-suite",
        "name": "Canopy Suite",
        "short_description": "Tree-framed windows and a private balcony above the mist.",
        "description": (
            "Wake to filtered forest light in our most spacious suite. A freestanding tub, "
            "writing desk, and balcony make this the ideal base for longer stays."
        ),
        "max_guests": 2,
        "beds": "King bed",
        "base_rate": 9800,
        "size_label": "42 m²",
        "size_sq_ft": 452,
        "amenities": [
            "Private balcony",
            "Rain shower & freestanding tub",
            "Forest view",
            "Mini pantry",
            "Workspace",
            "Climate control",
            "High-speed Wi‑Fi",
            "In-room safe",
        ],
        "included_services": [
            "Daily housekeeping",
            "Complimentary estate tea & filtered water",
            "Evening turndown on request",
            "Welcome amenity on arrival",
            "Access to Mist Spa & Forest Pool",
        ],
        "policies": [
            "Maximum occupancy: 2 adults",
            "Extra beds are not available in this suite",
            "Quiet hours from 10:00 PM to 7:00 AM",
            "Non-smoking room",
        ],
        "availability_note": "Two suites · often open midweek; weekends book 2–3 weeks ahead.",
        "image": "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1600&q=80"
        ],
        "sort_order": 1,
        "units": [
            {"code": "CS-01", "floor": "1", "status": "available", "housekeeping_status": "clean", "assignee": "Sofia Fernandes"},
            {"code": "CS-02", "floor": "1", "status": "ready", "housekeeping_status": "inspected", "assignee": "Sofia Fernandes"},
            {"code": "CS-03", "floor": "2", "status": "available", "housekeeping_status": "clean", "assignee": "Ravi Kumar"},
        ],
    },
    {
        "slug": "mist-cottage",
        "name": "Mist Cottage",
        "short_description": "A freestanding cottage with porch seating and garden path access.",
        "description": (
            "Freestanding cottage with porch seating and garden path access. "
            "Ideal for small families or guests who want a little extra space."
        ),
        "max_guests": 3,
        "beds": "Queen + daybed",
        "base_rate": 8500,
        "size_label": "38 m²",
        "size_sq_ft": 409,
        "amenities": ["Private porch", "Lounge nook", "Heated floors", "Garden access"],
        "included_services": ["Daily housekeeping", "Complimentary breakfast basket"],
        "policies": ["Maximum occupancy: 3 guests", "Non-smoking"],
        "availability_note": "Two cottages · popular on long weekends.",
        "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1400&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1400&q=80"
        ],
        "sort_order": 2,
        "units": [
            {"code": "MC-01", "floor": "G", "status": "available", "housekeeping_status": "clean", "assignee": "Sofia Fernandes"},
            {"code": "MC-02", "floor": "G", "status": "dirty", "housekeeping_status": "dirty", "assignee": "Ravi Kumar"},
            {"code": "MC-03", "floor": "G", "status": "available", "housekeeping_status": "clean", "assignee": "Ravi Kumar"},
        ],
    },
    {
        "slug": "leaf-room",
        "name": "Leaf Room",
        "short_description": "Calm lodge room with reading chair and canopy window seat.",
        "description": (
            "Calm lodge room with reading chair and canopy window seat. "
            "Our most accessible rate for solo travellers and couples."
        ),
        "max_guests": 2,
        "beds": "Queen bed",
        "base_rate": 6200,
        "size_label": "28 m²",
        "size_sq_ft": 301,
        "amenities": ["Window seat", "Reading chair", "Organic toiletries"],
        "included_services": ["Daily housekeeping", "Estate tea service"],
        "policies": ["Maximum occupancy: 2 guests", "Non-smoking"],
        "availability_note": "Four rooms · best availability midweek.",
        "image": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=1600&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=1600&q=80"
        ],
        "sort_order": 3,
        "units": [
            {"code": "LR-01", "floor": "2", "status": "available", "housekeeping_status": "clean", "assignee": "Sofia Fernandes"},
            {"code": "LR-02", "floor": "2", "status": "cleaning", "housekeeping_status": "in_progress", "assignee": "Sofia Fernandes"},
            {"code": "LR-03", "floor": "2", "status": "available", "housekeeping_status": "clean", "assignee": "Ravi Kumar"},
            {"code": "LR-04", "floor": "3", "status": "maintenance", "housekeeping_status": "dirty", "assignee": "Ravi Kumar", "notes": "Plumbing leak under repair"},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed room types and units shared by public website and staff dashboard."

    def handle(self, *args, **options):
        created_types = 0
        created_units = 0

        for data in ROOM_TYPES:
            payload = {**data}
            units = payload.pop("units")
            room_type, type_created = RoomType.objects.update_or_create(
                slug=payload["slug"],
                defaults=payload,
            )
            if type_created:
                created_types += 1
                self.stdout.write(self.style.SUCCESS(f"Created room type: {room_type.name}"))
            else:
                self.stdout.write(f"Updated room type: {room_type.name}")

            for unit_data in units:
                unit, unit_created = RoomUnit.objects.update_or_create(
                    code=unit_data["code"],
                    defaults={**unit_data, "room_type": room_type},
                )
                if unit_created:
                    created_units += 1
                    self.stdout.write(f"  + unit {unit.code}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Room types created: {created_types}, units created: {created_units}"
            )
        )
