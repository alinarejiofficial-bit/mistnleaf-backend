"""
Bridge published CMS content to Django website template context.
"""
from __future__ import annotations

import logging
import re

from django.utils.html import strip_tags

from apps.cms.services import cms_store_exists, read_published_cms_content
from apps.website.content import (
    AMENITIES,
    EXPERIENCES,
    FAQS,
    GALLERY_IMAGES,
    MEDIA,
    OFFERS,
    ROOMS,
    SITE,
    TESTIMONIALS,
    get_rooms,
)

logger = logging.getLogger(__name__)

ROOM_ID_SLUGS = {
    "cms-room-1": "canopy-suite",
    "cms-room-2": "mist-cottage",
    "cms-room-3": "leaf-room",
}

AMENITY_FALLBACK_IMAGES = [
    MEDIA.get("spa", ""),
    MEDIA.get("lounge", ""),
    MEDIA.get("pool", ""),
    MEDIA.get("yoga", ""),
    MEDIA.get("leaf_window", ""),
    MEDIA.get("forest_light", ""),
]


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "room"


def _load_published() -> dict | None:
    try:
        return read_published_cms_content()
    except Exception as exc:
        logger.warning("Failed to load published CMS: %s", exc)
        return None


def _use_static_fallback() -> bool:
    """Only fall back to hardcoded content when CMS was never seeded."""
    return not cms_store_exists()


def _pick_by_ids(items: list[dict], ids: list[str], limit: int) -> list[dict]:
    """Return items in featured-id order, then fill from remaining published items."""
    by_id = {str(item.get("id")): item for item in items if item.get("id")}
    by_slug = {item.get("slug"): item for item in items if item.get("slug")}
    featured: list[dict] = []
    for item_id in ids or []:
        item = by_id.get(str(item_id)) or by_slug.get(item_id)
        if item and item not in featured:
            featured.append(item)
    if len(featured) < limit:
        for item in items:
            if item not in featured:
                featured.append(item)
            if len(featured) >= limit:
                break
    return featured[:limit]


def _resolve_room_image(image: str, slug: str, static: dict) -> str:
    """Prefer CMS media URLs; fall back to packaged static art when missing/broken."""
    from apps.website.content import resolve_public_image

    candidate = (image or "").strip()
    fallback = static.get("image") or MEDIA.get("suite_bedroom", "")
    return resolve_public_image(candidate, fallback)


def _cms_room_to_dict(room: dict) -> dict:
    slug = ROOM_ID_SLUGS.get(room.get("id", ""), _slugify(room.get("name", "room")))
    images = [img for img in (room.get("images") or []) if isinstance(img, str) and img.strip()]
    static_by_slug = {r["slug"]: r for r in ROOMS}
    static = static_by_slug.get(slug, {})
    image = _resolve_room_image(images[0] if images else "", slug, static)
    gallery = images or static.get("gallery") or ([image] if image else [])
    cms_price = room.get("priceFrom")
    return {
        "slug": slug,
        "id": room.get("id"),
        "name": room.get("name", "") or static.get("name", ""),
        "short": room.get("tagline", "") or static.get("short", ""),
        "description": strip_tags(room.get("description", "")) or static.get("description", ""),
        "price": int(cms_price if cms_price not in (None, "") else static.get("price", 0)),
        "guests": int(room.get("capacity") or static.get("guests", 2)),
        "size": static.get("size", ""),
        "beds": static.get("beds", ""),
        "amenities": room.get("amenities") or static.get("amenities", []),
        "included_services": static.get("included_services", []),
        "availability": static.get("availability", ""),
        "policies": static.get("policies", []),
        "image": image,
        "gallery": gallery,
    }


def _merge_room_with_db(room: dict, db_by_slug: dict[str, dict] | None = None) -> dict:
    """Overlay CMS marketing copy onto live inventory fields."""
    try:
        lookup = db_by_slug if db_by_slug is not None else {item["slug"]: item for item in get_rooms()}
        db = lookup.get(room["slug"])
        if not db:
            return room
        merged = {
            **db,
            **{key: value for key, value in room.items() if value not in (None, "", [])},
        }
        merged["slug"] = db["slug"]
        # Prefer CMS marketing price/capacity when editors set them.
        if room.get("price") not in (None, ""):
            merged["price"] = room["price"]
        else:
            merged["price"] = db.get("price", 0)
        if room.get("guests") not in (None, ""):
            merged["guests"] = room["guests"]
        else:
            merged["guests"] = db.get("guests", 2)
        if db.get("image") and not merged.get("image"):
            merged["image"] = db["image"]
        if db.get("gallery") and not merged.get("gallery"):
            merged["gallery"] = db["gallery"]
        merged["id"] = room.get("id") or db.get("id")
        return merged
    except Exception:
        return room


def get_cms_rooms() -> list[dict]:
    """Public rooms come from live RoomType inventory, enriched with CMS copy."""
    live = get_rooms()
    db_by_slug = {item["slug"]: item for item in live}
    published = _load_published()
    cms_items = []
    if published:
        cms_items = [
            _cms_room_to_dict(room)
            for room in published.get("rooms", [])
            if (room.get("status") or "Published") == "Published"
        ]
    elif _use_static_fallback() and not live:
        return live

    cms_by_slug = {item["slug"]: item for item in cms_items if item.get("slug")}
    if live:
        result = [
            _merge_room_with_db(cms_by_slug.get(item["slug"], item), db_by_slug)
            for item in live
        ]
        # Include published CMS-only rooms that are not yet in inventory.
        seen = {item["slug"] for item in result}
        for cms_room in cms_items:
            slug = cms_room.get("slug")
            if slug and slug not in seen:
                result.append(cms_room)
                seen.add(slug)
        return result
    return [_merge_room_with_db(item, db_by_slug) for item in cms_items]


def get_cms_room(slug: str) -> dict | None:
    for room in get_cms_rooms():
        if room["slug"] == slug:
            return room
    return None


def get_cms_experiences() -> list[dict]:
    published = _load_published()
    if published is None and _use_static_fallback():
        return [{**item, "id": f"static-exp-{index}"} for index, item in enumerate(EXPERIENCES)]

    items = (published or {}).get("experiences")
    if items is None and _use_static_fallback():
        return [{**item, "id": f"static-exp-{index}"} for index, item in enumerate(EXPERIENCES)]

    static_by_title = {item["title"].lower(): item for item in EXPERIENCES}
    experiences = []
    for index, item in enumerate(sorted(items or [], key=lambda x: x.get("sortOrder", 0))):
        title = item.get("title", "")
        static = static_by_title.get(title.lower(), {})
        fallback_image = static.get("image") or EXPERIENCES[index % len(EXPERIENCES)]["image"]
        image = (item.get("imageUrl") or "").strip() or fallback_image or MEDIA.get("forest_walk", "")
        experiences.append(
            {
                "id": item.get("id"),
                "title": title,
                "duration": item.get("duration", "") or static.get("duration", ""),
                "description": item.get("description", "") or static.get("description", ""),
                "image": image,
            }
        )
    return experiences


def get_cms_homepage_bands() -> dict:
    published = _load_published() or {}
    homepage = published.get("homepage") or {}
    bands = homepage.get("bands") or {}

    def band(key: str, defaults: dict) -> dict:
        raw = bands.get(key) or {}
        status = raw.get("status", "Published")
        return {
            "eyebrow": raw.get("eyebrow", defaults.get("eyebrow", "")),
            "title": raw.get("title", defaults.get("title", "")),
            "lead": raw.get("lead", defaults.get("lead", "")),
            "view_all_label": raw.get("viewAllLabel", defaults.get("view_all_label", "")),
            "directions_label": raw.get("directionsLabel", defaults.get("directions_label", "")),
            "status": status,
            "visible": status == "Published",
        }

    return {
        "rooms": band(
            "rooms",
            {
                "eyebrow": "Stay",
                "title": "Featured Rooms",
                "lead": "Suites and cottages shaped for rest, with forest light and soft linens.",
                "view_all_label": "View all rooms",
            },
        ),
        "experiences": band(
            "experiences",
            {
                "eyebrow": "Do",
                "title": "Experiences",
                "lead": "Optional rituals for your stay — walks, tea, and quiet evenings.",
                "view_all_label": "All experiences",
            },
        ),
        "amenities": band(
            "amenities",
            {
                "eyebrow": "Comforts",
                "title": "Amenities",
                "lead": "Shared spaces for rest between walks, meals, and quiet hours.",
                "view_all_label": "Explore amenities",
            },
        ),
        "gallery": band(
            "gallery",
            {
                "eyebrow": "Look",
                "title": "A quiet visual diary",
                "lead": "Soft light through glass, mist in the trees, and rooms shaped for unhurried mornings.",
                "view_all_label": "Full gallery",
            },
        ),
        "offers": band(
            "offers",
            {
                "eyebrow": "Packages",
                "title": "Offers & Packages",
                "lead": "Thoughtful combinations of stay, meals, and experiences.",
                "view_all_label": "View offers",
            },
        ),
        "testimonials": band(
            "testimonials",
            {
                "eyebrow": "Guests",
                "title": "Guest Testimonials",
                "lead": "Words from travellers who stayed among the mist and leaves.",
            },
        ),
        "faqs": band(
            "faqs",
            {
                "eyebrow": "Help",
                "title": "Frequently asked questions",
                "lead": "Quick answers before you arrive — check-in, transfers, dining, and more.",
                "view_all_label": "View all FAQs",
            },
        ),
        "location": band(
            "location",
            {
                "eyebrow": "Location",
                "title": "Above the valley in Munnar",
                "lead": "Nestled near Whispering Pines — close enough to town, far enough for quiet.",
                "directions_label": "Get directions",
            },
        ),
    }


def get_homepage_section_visibility() -> dict:
    """Which homepage blocks should render on the public site."""
    published = _load_published() or {}
    homepage = published.get("homepage") or {}
    about = published.get("about") or {}
    bands = get_cms_homepage_bands()
    return {
        "hero": homepage.get("status", "Published") == "Published",
        "about": about.get("status", "Published") == "Published",
        "rooms": bands["rooms"]["visible"],
        "experiences": bands["experiences"]["visible"],
        "amenities": bands["amenities"]["visible"],
        "gallery": bands["gallery"]["visible"],
        "offers": bands["offers"]["visible"],
        "testimonials": bands["testimonials"]["visible"],
        "location": bands["location"]["visible"],
        "faqs": bands["faqs"]["visible"],
    }


def get_cms_amenities() -> list[dict]:
    published = _load_published()
    if published is None and _use_static_fallback():
        return [{**item, "id": f"static-amen-{index}"} for index, item in enumerate(AMENITIES)]

    items = (published or {}).get("amenities")
    if items is None and _use_static_fallback():
        return [{**item, "id": f"static-amen-{index}"} for index, item in enumerate(AMENITIES)]

    static_by_title = {item["title"].lower(): item for item in AMENITIES}
    amenities = []
    for index, item in enumerate(sorted(items or [], key=lambda x: x.get("sortOrder", 0))):
        title = item.get("title", "")
        static = static_by_title.get(title.lower(), {})
        fallback = (
            static.get("image")
            or AMENITY_FALLBACK_IMAGES[index % len(AMENITY_FALLBACK_IMAGES)]
            or MEDIA.get("spa", "")
        )
        amenities.append(
            {
                "id": item.get("id"),
                "title": title,
                "description": item.get("description", "") or static.get("description", ""),
                "image": (item.get("imageUrl") or "").strip() or fallback,
            }
        )
    return amenities


def get_cms_gallery() -> list[dict]:
    """All published gallery images for the Gallery page."""
    published = _load_published()
    if published is None and _use_static_fallback():
        return [{**item, "id": f"static-{index}"} for index, item in enumerate(GALLERY_IMAGES)]

    items = (published or {}).get("galleryImages")
    if not items:
        return (
            [{**item, "id": f"static-{index}"} for index, item in enumerate(GALLERY_IMAGES)]
            if _use_static_fallback()
            else []
        )

    gallery = []
    for index, item in enumerate(sorted(items, key=lambda x: x.get("sortOrder", 0))):
        fallback = GALLERY_IMAGES[index % len(GALLERY_IMAGES)] if GALLERY_IMAGES else {}
        src = (item.get("imageUrl") or "").strip() or fallback.get("src") or MEDIA.get("hero", "")
        gallery.append(
            {
                "id": item.get("id"),
                "src": src,
                "alt": item.get("title") or fallback.get("alt", ""),
                "label": item.get("caption") or item.get("title") or fallback.get("label", ""),
            }
        )
    return gallery or (
        [{**item, "id": f"static-{index}"} for index, item in enumerate(GALLERY_IMAGES)]
        if _use_static_fallback()
        else []
    )


def get_cms_offers() -> list[dict]:
    """All published offers for the Offers page."""
    published = _load_published()
    if published is None and _use_static_fallback():
        return [{**item, "id": f"static-offer-{index}"} for index, item in enumerate(OFFERS)]
    items = (published or {}).get("offers")
    if items is None and _use_static_fallback():
        return [{**item, "id": f"static-offer-{index}"} for index, item in enumerate(OFFERS)]
    return [
        {
            "id": item.get("id"),
            "title": item.get("title", ""),
            "detail": strip_tags(item.get("description", "")),
            "valid": " · ".join(item.get("terms") or []) or strip_tags(item.get("details", "")),
            "price_from": int(item.get("priceFrom", 0) or 0),
        }
        for item in sorted(items or [], key=lambda x: x.get("sortOrder", 0))
    ]


def get_cms_testimonials() -> list[dict]:
    published = _load_published()
    if published is None and _use_static_fallback():
        return [{**item, "id": f"static-tst-{index}"} for index, item in enumerate(TESTIMONIALS)]
    items = (published or {}).get("testimonials")
    if items is None and _use_static_fallback():
        return [{**item, "id": f"static-tst-{index}"} for index, item in enumerate(TESTIMONIALS)]

    def initials(name: str, fallback: str = "") -> str:
        if fallback:
            return fallback
        parts = [p for p in re.split(r"[\s&]+", name or "") if p]
        chars = "".join(p[0] for p in parts if p)
        return (chars[:2] or "?").upper()

    return [
        {
            "id": item.get("id"),
            "quote": item.get("content", ""),
            "name": item.get("guestName", ""),
            "place": item.get("guestLocation", ""),
            "initials": initials(item.get("guestName", ""), item.get("initials", "")),
        }
        for item in items or []
    ]


def get_cms_faqs() -> list[dict]:
    published = _load_published()
    if published is None and _use_static_fallback():
        return [{**item, "id": f"static-faq-{index}"} for index, item in enumerate(FAQS)]
    items = (published or {}).get("faqs")
    if items is None and _use_static_fallback():
        return [{**item, "id": f"static-faq-{index}"} for index, item in enumerate(FAQS)]
    return [
        {
            "id": item.get("id"),
            "q": item.get("question", ""),
            "a": item.get("answer", ""),
        }
        for item in sorted(items or [], key=lambda x: x.get("sortOrder", 0))
    ]


def get_cms_homepage() -> dict:
    published = _load_published() or {}
    homepage = published.get("homepage") or {}
    return {
        "eyebrow": homepage.get("heroEyebrow", "Staycation"),
        "title": homepage.get("heroHeadline", SITE["tagline"]),
        "lead": homepage.get("heroDescription", SITE["description"]),
        "hero_media": homepage.get("heroMediaUrl") or MEDIA["hero"],
        "cta_primary": homepage.get("heroCtaPrimary", "Book your stay"),
        "cta_secondary": homepage.get("heroCtaSecondary", "Explore rooms"),
        "featured_room_ids": homepage.get("featuredRoomIds", []),
        "featured_offer_ids": homepage.get("featuredOfferIds", []),
        "featured_experience_ids": homepage.get("featuredExperienceIds", []),
        "featured_amenity_ids": homepage.get("featuredAmenityIds", []),
        "featured_testimonial_ids": homepage.get("featuredTestimonialIds", []),
        "homepage_gallery_image_ids": homepage.get("homepageGalleryImageIds", []),
        "homepage_faq_ids": homepage.get("homepageFaqIds", []),
    }


def get_cms_about() -> dict:
    published = _load_published() or {}
    about = published.get("about") or {}
    contact = get_cms_contact()
    site = get_cms_site()

    content = about.get("content", "") or ""
    story_html = (about.get("storyHtml") or "").strip() or content
    title = (about.get("title") or "").strip() or "Soft light, quiet rooms, forest air"
    lead = (about.get("lead") or "").strip() or (
        "A small retreat above the Munnar valley — shaped by mist, leaf, and "
        "the wish for unhurried days."
    )

    default_pillars = [
        {
            "id": "about-pillar-1",
            "title": "Intentionally small",
            "copy": "Fewer rooms mean quieter mornings, closer care, and a stay that never feels hurried.",
        },
        {
            "id": "about-pillar-2",
            "title": "Forest first",
            "copy": "Paths, mist, and canopy light shape the day — we build around the landscape, not over it.",
        },
        {
            "id": "about-pillar-3",
            "title": "Personal hospitality",
            "copy": "Meals, walks, and quiet hours arranged with attention, not a script.",
        },
    ]
    pillars_raw = about.get("pillars") or default_pillars
    pillars = []
    for index, pillar in enumerate(pillars_raw[:3]):
        pillars.append(
            {
                "index": f"{index + 1:02d}",
                "title": pillar.get("title", ""),
                "copy": pillar.get("copy", ""),
            }
        )

    mosaic_fallbacks = [
        {"src": MEDIA.get("tea_estate", ""), "caption": "Tea hills beyond the lodge"},
        {"src": MEDIA.get("leaf_bedroom", ""), "caption": "Canopy light indoors"},
        {"src": MEDIA.get("hero", ""), "caption": "Valley mist at dusk"},
    ]
    mosaic = []
    for index, item in enumerate((about.get("mosaic") or mosaic_fallbacks)[:3]):
        fallback = mosaic_fallbacks[index % len(mosaic_fallbacks)]
        mosaic.append(
            {
                "src": (item.get("imageUrl") or "").strip() or fallback["src"],
                "caption": item.get("caption") or fallback["caption"],
                "alt": item.get("caption") or fallback["caption"],
            }
        )

    place_lead = (about.get("placeLead") or "").strip()
    if not place_lead:
        place_lead = f"{site['address']['line1']}\n{site['address']['line2']}"

    return {
        "eyebrow": about.get("eyebrow", "About Mistnleaf"),
        "page_eyebrow": about.get("pageEyebrow") or "Our story",
        "title": title,
        "lead": lead,
        "content_html": content,
        "story_eyebrow": about.get("storyEyebrow") or "Beginnings",
        "story_title": about.get("storyTitle") or "Rebuilt slowly for quieter stays",
        "story_html": story_html,
        "story_image": (about.get("storyImageUrl") or "").strip() or MEDIA.get("forest_walk", ""),
        "pillars_eyebrow": about.get("pillarsEyebrow") or "How we host",
        "pillars_title": about.get("pillarsTitle") or "What we keep close",
        "pillars": pillars,
        "atmosphere_eyebrow": about.get("atmosphereEyebrow") or "Atmosphere",
        "atmosphere_title": about.get("atmosphereTitle") or "Light through glass, mist in the trees",
        "atmosphere_lead": about.get("atmosphereLead")
        or "Lodge mornings, tea-hill afternoons, and evenings when the valley softens into fog.",
        "mosaic": mosaic,
        "place_eyebrow": about.get("placeEyebrow") or "Find us",
        "place_title": about.get("placeTitle") or "Above the valley in Munnar",
        "place_lead": place_lead,
        "place_meta": about.get("placeMeta") or site.get("hours", ""),
        "place_cta_label": about.get("placeCtaLabel") or "Book your stay",
        "place_directions_label": about.get("placeDirectionsLabel") or "Get directions",
        "place_image": (about.get("placeImageUrl") or "").strip()
        or MEDIA.get("cottage_exterior", ""),
        "image": (about.get("imageUrl") or "").strip() or MEDIA["about_lodge"],
        "cta_label": about.get("ctaLabel", "Read our story"),
        "status": about.get("status", "Published"),
        "email": contact["email"],
        "phone": contact["phone"],
    }


def get_cms_contact() -> dict:
    published = _load_published() or {}
    contact = published.get("contact") or {}
    default_address = f"{SITE['address']['line1']}, {SITE['address']['line2']}"
    return {
        "email": contact.get("email") or SITE["email"],
        "phone": contact.get("phone") or SITE["phone"],
        "address": contact.get("address") or default_address,
        "whatsapp": contact.get("whatsapp", ""),
        "check_in_note": contact.get("checkInNote", ""),
        "status": contact.get("status", "Published"),
    }


def get_cms_location() -> dict:
    published = _load_published() or {}
    location = published.get("location") or {}
    bands = get_cms_homepage_bands()["location"]
    return {
        "title": location.get("title") or bands.get("title") or "Above the valley in Munnar",
        "description": location.get("description") or bands.get("lead", ""),
        "address": location.get("address", ""),
        "airport_note": location.get("airportNote", "~3.5–4 hrs from COK"),
        "directions_url": location.get("directionsUrl", ""),
        "status": location.get("status", "Published"),
    }


def _normalize_footer_links(links: list | None, defaults: list[dict]) -> list[dict]:
    """Map CMS footer links (often homepage hashes) onto real site paths."""
    path_aliases = {
        "#offers": "/offers/",
        "#faqs": "/faqs/",
        "#contact": "/contact/",
        "#book": "/booking/search/",
        "#rooms": "/rooms/",
        "#experiences": "/experiences/",
        "#amenities": "/amenities/",
        "#dining": "/dining/",
        "#gallery": "/gallery/",
        "#location": "/location/",
        "#about": "/about/",
        "/offers": "/offers/",
        "/faqs": "/faqs/",
        "/contact": "/contact/",
        "/booking/search": "/booking/search/",
        "/things-to-do": "/things-to-do/",
        "/explore": "/explore/",
        "/about": "/about/",
        "/rooms": "/rooms/",
        "/experiences": "/experiences/",
        "/amenities": "/amenities/",
        "/dining": "/dining/",
        "/gallery": "/gallery/",
        "/location": "/location/",
        "/privacy": "/privacy/",
        "/terms": "/terms/",
        "/cancellation": "/cancellation/",
    }
    label_aliases = {
        "offers": "/offers/",
        "faqs": "/faqs/",
        "contact": "/contact/",
        "contact / enquiry": "/contact/",
        "check availability": "/booking/search/",
        "things to do": "/things-to-do/",
        "site guide": "/explore/",
        "about": "/about/",
        "rooms": "/rooms/",
        "experiences": "/experiences/",
        "amenities": "/amenities/",
        "dining": "/dining/",
        "gallery": "/gallery/",
    }

    source = links if links else defaults
    normalized: list[dict] = []
    for item in source:
        label = (item.get("label") or "").strip()
        href = (item.get("href") or "").strip()
        mapped = path_aliases.get(href) or label_aliases.get(label.lower())
        if mapped:
            href = mapped
        elif href.startswith("#"):
            continue
        elif href.startswith("/") and not href.endswith("/"):
            href = f"{href}/"
        if not href or not label:
            continue
        normalized.append({"label": label, "href": href})
    return normalized or defaults


def get_cms_footer() -> dict:
    published = _load_published() or {}
    footer = published.get("footer") or {}
    contact = get_cms_contact()
    default_explore = [
        {"label": "About", "href": "/about/"},
        {"label": "Rooms", "href": "/rooms/"},
        {"label": "Experiences", "href": "/experiences/"},
        {"label": "Gallery", "href": "/gallery/"},
    ]
    default_plan = [
        {"label": "Offers", "href": "/offers/"},
        {"label": "FAQs", "href": "/faqs/"},
        {"label": "Contact", "href": "/contact/"},
        {"label": "Check availability", "href": "/booking/search/"},
    ]
    return {
        "brand_eyebrow": footer.get("brandEyebrow", SITE["name"]),
        "brand_description": (footer.get("brandDescription") or "").strip() or SITE["description"],
        "tagline": (footer.get("tagline") or "").strip() or SITE["tagline"],
        "copyright": footer.get("copyright") or f"© {SITE['name']}. Nature in every breath.",
        "explore_links": _normalize_footer_links(footer.get("exploreLinks"), default_explore),
        "plan_links": _normalize_footer_links(footer.get("planLinks"), default_plan),
        "policy_links": _normalize_footer_links(
            footer.get("policyLinks"),
            [
                {"label": "Privacy Policy", "href": "/privacy/"},
                {"label": "Terms & Conditions", "href": "/terms/"},
                {"label": "Cancellation Policy", "href": "/cancellation/"},
            ],
        ),
        "staff_login_label": footer.get("staffLoginLabel", ""),
        "staff_login_href": footer.get("staffLoginHref", ""),
        "status": footer.get("status", "Published"),
        "email": contact["email"],
        "phone": contact["phone"],
        "address": contact["address"],
    }


def get_cms_social() -> dict:
    published = _load_published() or {}
    social = published.get("social") or {}
    return {
        "instagram": social.get("instagram", ""),
        "facebook": social.get("facebook", ""),
        "twitter": social.get("twitter", ""),
        "youtube": social.get("youtube", ""),
        "linkedin": social.get("linkedin", ""),
        "status": social.get("status", "Published"),
    }


def get_cms_site() -> dict:
    contact = get_cms_contact()
    footer = get_cms_footer()
    address_lines = [line.strip() for line in contact["address"].splitlines() if line.strip()]
    return {
        **SITE,
        "tagline": footer["tagline"] or SITE["tagline"],
        "description": footer["brand_description"] or SITE["description"],
        "email": contact["email"],
        "phone": contact["phone"],
        "address": {
            "line1": address_lines[0] if address_lines else SITE["address"]["line1"],
            "line2": (
                ", ".join(address_lines[1:])
                if len(address_lines) > 1
                else SITE["address"]["line2"]
            ),
            "country": SITE["address"].get("country", "India"),
        },
    }


def featured_cms_rooms(limit: int = 3) -> list[dict]:
    homepage = get_cms_homepage()
    return _pick_by_ids(get_cms_rooms(), homepage.get("featured_room_ids", []), limit)


def featured_cms_gallery(limit: int = 7) -> list[dict]:
    homepage = get_cms_homepage()
    published = get_cms_gallery()
    ids = [item_id for item_id in (homepage.get("homepage_gallery_image_ids") or []) if item_id]
    if not ids:
        return published[:limit]
    by_id = {item.get("id"): item for item in published if item.get("id")}
    return [by_id[item_id] for item_id in ids if item_id in by_id][:limit]


def featured_cms_offers(limit: int = 3) -> list[dict]:
    homepage = get_cms_homepage()
    return _pick_by_ids(get_cms_offers(), homepage.get("featured_offer_ids", []), limit)


def featured_cms_experiences(limit: int = 4) -> list[dict]:
    homepage = get_cms_homepage()
    return _pick_by_ids(get_cms_experiences(), homepage.get("featured_experience_ids", []), limit)


def featured_cms_amenities(limit: int = 3) -> list[dict]:
    homepage = get_cms_homepage()
    return _pick_by_ids(get_cms_amenities(), homepage.get("featured_amenity_ids", []), limit)


def featured_cms_testimonials(limit: int = 3) -> list[dict]:
    homepage = get_cms_homepage()
    return _pick_by_ids(get_cms_testimonials(), homepage.get("featured_testimonial_ids", []), limit)


def featured_cms_faqs(limit: int = 4) -> list[dict]:
    homepage = get_cms_homepage()
    published = get_cms_faqs()
    ids = [item_id for item_id in (homepage.get("homepage_faq_ids") or []) if item_id]
    if not ids:
        return published[:limit]
    by_id = {item.get("id"): item for item in published if item.get("id")}
    return [by_id[item_id] for item_id in ids if item_id in by_id][:limit]
