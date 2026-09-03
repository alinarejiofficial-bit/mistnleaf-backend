"""Site content and media URLs for the public Django website."""

from __future__ import annotations

from decimal import Decimal


def unsplash(photo_id: str, width: int = 1600) -> str:
    return f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w={width}&q=80"


MEDIA = {
    "logo": "/static/website/images/mistnleaf-logo.png",
    "logo_light": "/static/website/images/mistnleaf-logo-light.png",
    "hero": unsplash("photo-1470071459604-3b5ec3a7fe05", 2000),
    "about_lodge": unsplash("photo-1566073771259-6a8506099945", 1400),
    "location_hills": unsplash("photo-1464822759023-fed622ff2c3b", 1400),
    "cottage_exterior": unsplash("photo-1520250497591-112f2f40a3f4", 1400),
    "suite_bedroom": unsplash("photo-1590490360182-c33d57733427", 1600),
    "suite_bath": unsplash("photo-1582719478250-c89cae4dc85b", 1200),
    "suite_balcony": unsplash("photo-1590490360182-c33d57733427", 1200),
    "leaf_bedroom": unsplash("photo-1631049307264-da0ec9d70304", 1600),
    "forest_walk": unsplash("photo-1448375240586-882707db888b", 1400),
    "tea_estate": unsplash("photo-1464822759023-fed622ff2c3b", 1400),
    "fireside": unsplash("photo-1517248135467-4c7edcad34c4", 1400),
    "botanical": unsplash("photo-1466692476866-aef1dfb1e735", 1400),
    "spa": unsplash("photo-1544161515-4ab6ce6db874", 1200),
    "lounge": unsplash("photo-1618221195710-dd6b41faaea6", 1200),
    "pool": unsplash("photo-1576013551627-0cc20b96c2a7", 1200),
    "yoga": unsplash("photo-1544367567-0f2fcb009e0b", 1200),
    "dining": unsplash("photo-1559339352-11d035aa65de", 1600),
    "forest_light": unsplash("photo-1448375240586-882707db888b", 1400),
    "leaf_window": unsplash("photo-1595576508898-0ad5c879a061", 1200),
}

SITE = {
    "name": "Mistnleaf",
    "tagline": "Nature in Every Breath",
    "description": (
        "Mistnleaf Staycation is a forest retreat where slow mornings, soft light, "
        "and thoughtful hospitality meet."
    ),
    "email": "info@mistnleaf.com",
    "phone": "+91 98765 43210",
    "address": {
        "line1": "Hill Road, Near Whispering Pines",
        "line2": "Munnar, Kerala 685612",
        "country": "India",
    },
    "hours": "Front desk · 8:00 AM – 10:00 PM",
}

NAV_LINKS = [
    {"href": "/about/", "label": "About"},
    {"href": "/rooms/", "label": "Rooms"},
    {"href": "/experiences/", "label": "Experiences"},
    {"href": "/amenities/", "label": "Amenities"},
    {"href": "/gallery/", "label": "Gallery"},
    {"href": "/things-to-do/", "label": "Activities"},
    {"href": "/location/", "label": "Location"},
    {"href": "/contact/", "label": "Contact"},
]

ROOMS = [
    {
        "slug": "canopy-suite",
        "name": "Canopy Suite",
        "short": "Tree-framed windows and a private balcony above the mist.",
        "description": (
            "Wake to filtered forest light in our most spacious suite. A freestanding tub, "
            "writing desk, and balcony make this the ideal base for longer stays."
        ),
        "price": 9800,
        "guests": 2,
        "size": "42 m²",
        "beds": "King bed",
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
        "availability": "Two suites · often open midweek; weekends book 2–3 weeks ahead.",
        "policies": [
            "Maximum occupancy: 2 adults",
            "Extra beds are not available in this suite",
            "Quiet hours from 10:00 PM to 7:00 AM",
            "Non-smoking room",
        ],
        "image": MEDIA["suite_bedroom"],
        "gallery": [MEDIA["suite_bedroom"], MEDIA["suite_balcony"], MEDIA["suite_bath"]],
    },
    {
        "slug": "mist-cottage",
        "name": "Mist Cottage",
        "short": "A freestanding cottage wrapped in morning fog and ferns.",
        "description": (
            "Tucked a short walk from the main lodge, Mist Cottage offers privacy, "
            "a wood-accented lounge, and a porch made for tea at dusk."
        ),
        "price": 8500,
        "guests": 3,
        "size": "38 m²",
        "beds": "Queen + daybed",
        "amenities": [
            "Private porch",
            "Lounge nook",
            "Garden path access",
            "Heated floors",
            "Outdoor seating",
            "Rain shower",
            "High-speed Wi‑Fi",
            "Mini pantry",
        ],
        "included_services": [
            "Daily housekeeping",
            "Complimentary estate tea & filtered water",
            "Porch breakfast setup on request",
            "Welcome amenity on arrival",
            "Access to Mist Spa & Forest Pool",
        ],
        "availability": "One cottage · limited inventory; reserve early for peak season.",
        "policies": [
            "Maximum occupancy: 2 adults + 1 child (daybed)",
            "Children welcome with advance notice for bedding",
            "Quiet hours from 10:00 PM to 7:00 AM",
            "Non-smoking cottage",
        ],
        "image": MEDIA["cottage_exterior"],
        "gallery": [MEDIA["cottage_exterior"]],
    },
    {
        "slug": "leaf-room",
        "name": "Leaf Room",
        "short": "A calm lodge room with soft greens and curated quiet.",
        "description": (
            "Compact and carefully composed — linen bedding, a reading chair, "
            "and a window seat that looks into the canopy."
        ),
        "price": 6200,
        "guests": 2,
        "size": "28 m²",
        "beds": "Queen bed",
        "amenities": [
            "Window seat",
            "Reading chair",
            "Rain shower",
            "Organic toiletries",
            "Blackout drapes",
            "High-speed Wi‑Fi",
            "Climate control",
            "Wardrobe space",
        ],
        "included_services": [
            "Daily housekeeping",
            "Complimentary estate tea & filtered water",
            "Welcome amenity on arrival",
            "Access to Mist Spa & Forest Pool",
            "Library Lounge access",
        ],
        "availability": "Two rooms · flexible dates midweek; weekends fill first.",
        "policies": [
            "Maximum occupancy: 2 guests",
            "Extra beds are not available in this room",
            "Quiet hours from 10:00 PM to 7:00 AM",
            "Non-smoking room",
        ],
        "image": MEDIA["leaf_bedroom"],
        "gallery": [MEDIA["leaf_bedroom"], MEDIA["leaf_window"]],
    },
]

EXPERIENCES = [
    {"title": "Dawn Forest Walk", "duration": "90 minutes", "description": "A guided walk through misted trails with a naturalist.", "image": MEDIA["forest_walk"]},
    {"title": "Tea Estate Afternoon", "duration": "Half day", "description": "Visit a nearby estate and finish with a tasting on the veranda.", "image": MEDIA["tea_estate"]},
    {"title": "Fireside Story Hour", "duration": "Evenings", "description": "Seasonal evenings by the hearth with local stories and warm drinks.", "image": MEDIA["fireside"]},
    {"title": "Botanical Workshop", "duration": "2 hours", "description": "Press leaves, mix herbal infusions, and take home a keepsake.", "image": MEDIA["botanical"]},
]

AMENITIES = [
    {"title": "Mist Spa", "description": "Treatments using local botanicals in a quiet treatment room.", "image": MEDIA["spa"]},
    {"title": "Library Lounge", "description": "Deep chairs, travel writing, and board games by the window.", "image": MEDIA["lounge"]},
    {"title": "Forest Pool", "description": "A heated outdoor pool edged by ferns and stone.", "image": MEDIA["pool"]},
    {"title": "Yoga Deck", "description": "Morning sessions open to the canopy and cool air.", "image": MEDIA["yoga"]},
    {"title": "Work Nook", "description": "Reliable wifi and a calm desk space when you need it.", "image": MEDIA["leaf_window"]},
    {"title": "Garden Paths", "description": "Self-guided trails through moss, bamboo, and wildflowers.", "image": MEDIA["forest_light"]},
]

GALLERY_IMAGES = [
    {"src": MEDIA["about_lodge"], "alt": "Glass lodge above the misted valley", "label": "The lodge"},
    {"src": MEDIA["suite_bedroom"], "alt": "Canopy Suite opening to forest light", "label": "Canopy Suite"},
    {"src": MEDIA["cottage_exterior"], "alt": "Mist Cottage among ferns and water", "label": "Mist Cottage"},
    {"src": MEDIA["forest_walk"], "alt": "Dawn walk through misted forest trails", "label": "Forest trail"},
    {"src": MEDIA["leaf_bedroom"], "alt": "Leaf Room window over the hills", "label": "Leaf Room"},
    {"src": MEDIA["tea_estate"], "alt": "Tea estate afternoon on the lawn", "label": "Tea estate"},
    {"src": MEDIA["fireside"], "alt": "Fireside evening under the open sky", "label": "Fireside"},
    {"src": MEDIA["pool"], "alt": "Forest pool edged by stone and plants", "label": "Forest pool"},
    {"src": MEDIA["dining"], "alt": "Seasonal dining at Fern Kitchen", "label": "Fern Kitchen"},
    {"src": MEDIA["hero"], "alt": "Fog settling over the valley", "label": "Valley mist"},
]

OFFERS = [
    {"title": "Two Nights in the Mist", "detail": "Stay two nights and receive a complimentary forest walk for two.", "valid": "Valid weekdays · excludes peak weekends", "price_from": 11400},
    {"title": "Leaf & Table", "detail": "Room plus a three-course dinner at Fern Kitchen on one evening.", "valid": "Available year-round with advance notice", "price_from": 8900},
    {"title": "Long Stay Soft Landing", "detail": "Five nights or more includes daily breakfast and late checkout.", "valid": "Subject to availability", "price_from": 5600},
]

TESTIMONIALS = [
    {
        "quote": "Waking to mist in the trees felt like the world had gone quiet just for us. We will be back.",
        "name": "Ananya R.",
        "place": "Bengaluru",
        "initials": "AR",
    },
    {
        "quote": "The Canopy Suite, the forest walk, and dinner at Fern Kitchen — every detail was unhurried and warm.",
        "name": "James & Priya",
        "place": "Singapore",
        "initials": "JP",
    },
    {
        "quote": "A rare stay where the landscape does most of the talking. Soft light, kind staff, deep rest.",
        "name": "Meera S.",
        "place": "Kochi",
        "initials": "MS",
    },
]

FAQS = [
    {"q": "What is the check-in and check-out time?", "a": "Check-in is from 2:00 PM and check-out is by 11:00 AM."},
    {"q": "Do you offer airport or railway transfers?", "a": "Yes. Private transfers can be arranged at the time of booking."},
    {"q": "Are children welcome?", "a": "Children are welcome in Mist Cottage and select rooms."},
    {"q": "Is dining included?", "a": "Breakfast is included with most packages."},
    {"q": "What is your pet policy?", "a": "We are not able to host pets at this time, except trained service animals with prior notice."},
    {"q": "How do I modify or cancel a reservation?", "a": "Please review our Cancellation Policy and email stay@mistnleaf.com."},
]

DINING = {
    "intro": "Fern Kitchen serves seasonal plates rooted in local produce — quiet breakfasts, lingering lunches, and candlelit dinners.",
    "meals": [
        {"name": "Breakfast", "time": "7:30 – 10:30 AM", "note": "Fresh fruit, house breads, eggs to order, and estate tea."},
        {"name": "Lunch", "time": "12:30 – 3:00 PM", "note": "Light bowls, salads, and a daily regional special."},
        {"name": "Dinner", "time": "7:00 – 10:00 PM", "note": "A short tasting menu that changes with the harvest."},
    ],
    "image": MEDIA["dining"],
}

THINGS_TO_DO = [
    {"title": "Eravikulam National Park", "distance": "45 minutes", "description": "Protected grasslands and mountain views on a guided day trip."},
    {"title": "Attukal Waterfalls", "distance": "30 minutes", "description": "A short drive to cascading water after monsoon rains."},
    {"title": "Local Spice Markets", "distance": "20 minutes", "description": "Browse cardamom, pepper, and handmade crafts in town."},
    {"title": "Sunrise Viewpoint", "distance": "15 minutes", "description": "Catch first light over the valley — we can arrange an early transfer."},
]

BOOKING_STEPS = [
    {"key": "search", "label": "Search", "href": "/booking/search/"},
    {"key": "availability", "label": "Dates", "href": "/booking/availability/"},
    {"key": "select", "label": "Room", "href": "/booking/select/"},
    {"key": "addons", "label": "Add-ons", "href": "/booking/add-ons/"},
    {"key": "guest", "label": "Guest", "href": "/booking/guest/"},
    {"key": "summary", "label": "Price", "href": "/booking/summary/"},
    {"key": "payment", "label": "Pay", "href": "/booking/payment/"},
]


def format_inr(amount) -> str:
    value = int(Decimal(str(amount)))
    return f"₹{value:,}"


def get_room(slug: str) -> dict | None:
    for room in get_rooms():
        if room["slug"] == slug:
            return room
    return None


def resolve_public_image(image: str | None, fallback: str = "") -> str:
    """Prefer live media / remote URLs; skip missing admin-only asset paths."""
    value = (image or "").strip()
    if not value:
        return fallback
    if value.startswith(("http://", "https://")):
        return value
    if value.startswith("/media/") or value.startswith("media/"):
        return value if value.startswith("/") else f"/{value}"
    if value.startswith("/static/") or value.startswith("static/"):
        return value if value.startswith("/") else f"/{value}"
    # Seeded admin paths like /images/... are not served by Django.
    return fallback or value


def room_type_to_public_dict(room_type) -> dict:
    """Map a live RoomType to the public website room shape."""
    static = next((item for item in ROOMS if item["slug"] == room_type.slug), {})
    size = room_type.size_label or static.get("size") or (
        f"{room_type.size_sq_ft} sq ft" if room_type.size_sq_ft else ""
    )
    fallback_image = static.get("image") or MEDIA.get("suite_bedroom", "")
    image = resolve_public_image(room_type.image, fallback_image)
    raw_gallery = room_type.gallery or static.get("gallery") or ([image] if image else [])
    gallery = [
        resolve_public_image(item, image)
        for item in raw_gallery
        if isinstance(item, str) and item.strip()
    ] or ([image] if image else [])
    return {
        "slug": room_type.slug,
        "id": str(room_type.id),
        "name": room_type.name or static.get("name", ""),
        "short": room_type.short_description or static.get("short", ""),
        "description": room_type.description or static.get("description", ""),
        "price": int(room_type.base_rate),
        "guests": room_type.max_guests,
        "size": size,
        "beds": room_type.beds or static.get("beds", ""),
        "amenities": room_type.amenities or static.get("amenities", []),
        "included_services": room_type.included_services or static.get("included_services", []),
        "availability": room_type.availability_note or static.get("availability", ""),
        "policies": room_type.policies or static.get("policies", []),
        "image": image,
        "gallery": gallery,
    }


def get_rooms() -> list[dict]:
    """Live inventory first; fall back to static marketing rooms if none exist."""
    try:
        from apps.rooms.models import RoomType

        types = list(RoomType.objects.filter(is_active=True).order_by("sort_order", "name"))
    except Exception:
        types = []

    if types:
        return [room_type_to_public_dict(room_type) for room_type in types]
    return [dict(room) for room in ROOMS]
