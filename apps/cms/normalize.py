"""CMS content normalization — mirrors mistnleaf_admin/src/lib/cms-normalize.ts"""
from __future__ import annotations

import re
from copy import deepcopy

from .defaults import default_cms_content


def _parse_terms_from_details(details: str) -> list[str]:
    text = re.sub(r"<[^>]+>", " ", details or "")
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    return [part.strip().upper() for part in re.split(r"[·|]", text) if part.strip()]


def _migrate_experiences(items: list[dict]) -> list[dict]:
    migrated = []
    for index, item in enumerate(items):
        migrated.append(
            {
                **item,
                "duration": item.get("duration") or "—",
                "sortOrder": item.get("sortOrder", index),
            }
        )
    return migrated


def _normalize_offer(offer: dict, index: int) -> dict:
    terms = offer.get("terms") or []
    if not terms:
        terms = _parse_terms_from_details(offer.get("details", ""))
    return {
        **offer,
        "priceFrom": offer.get("priceFrom", 0),
        "priceLabel": offer.get("priceLabel", "FROM"),
        "terms": terms,
        "bookCtaLabel": offer.get("bookCtaLabel", "Book package →"),
        "bookCtaHref": offer.get("bookCtaHref", "#contact"),
        "sortOrder": offer.get("sortOrder", index),
    }


def _normalize_footer(raw: dict | None) -> dict:
    defaults = default_cms_content()["footer"]
    merged = {**defaults, **(raw or {})}
    return {
        **merged,
        "brandEyebrow": (raw or {}).get("brandEyebrow", defaults["brandEyebrow"]),
        "brandDescription": (raw or {}).get("brandDescription")
        or (raw or {}).get("tagline")
        or defaults["brandDescription"],
        "exploreLinks": (raw or {}).get("exploreLinks") or defaults["exploreLinks"],
        "planLinks": (raw or {}).get("planLinks") or defaults["planLinks"],
        "policyLinks": (raw or {}).get("policyLinks") or defaults["policyLinks"],
    }


def normalize_cms_content(raw: dict) -> dict:
    defaults = default_cms_content()
    legacy_homepage = raw.get("homepage") or {}

    if raw.get("experiences"):
        experiences = _migrate_experiences(raw["experiences"])
    elif legacy_homepage.get("experiences"):
        experiences = _migrate_experiences(legacy_homepage["experiences"])
    else:
        experiences = deepcopy(defaults["experiences"])

    default_bands = defaults["homepage"].get("bands") or {}
    legacy_bands = legacy_homepage.get("bands") or {}

    def merge_band(key: str) -> dict:
        merged = {**(default_bands.get(key) or {}), **(legacy_bands.get(key) or {})}
        if merged.get("status") not in ("Published", "Draft"):
            merged["status"] = (default_bands.get(key) or {}).get("status", "Published")
        return merged

    homepage = {
        **defaults["homepage"],
        **legacy_homepage,
        "heroEyebrow": legacy_homepage.get("heroEyebrow")
        or legacy_homepage.get("introductionTitle")
        or defaults["homepage"]["heroEyebrow"],
        "heroCtaPrimary": legacy_homepage.get("heroCtaPrimary", defaults["homepage"]["heroCtaPrimary"]),
        "heroCtaSecondary": legacy_homepage.get("heroCtaSecondary", defaults["homepage"]["heroCtaSecondary"]),
        "featuredExperienceIds": legacy_homepage.get(
            "featuredExperienceIds",
            defaults["homepage"].get("featuredExperienceIds", []),
        ),
        "featuredAmenityIds": legacy_homepage.get(
            "featuredAmenityIds",
            defaults["homepage"].get("featuredAmenityIds", []),
        ),
        "featuredTestimonialIds": legacy_homepage.get(
            "featuredTestimonialIds",
            defaults["homepage"].get("featuredTestimonialIds", []),
        ),
        "homepageGalleryImageIds": legacy_homepage.get(
            "homepageGalleryImageIds",
            defaults["homepage"].get("homepageGalleryImageIds", []),
        ),
        "homepageFaqIds": legacy_homepage.get(
            "homepageFaqIds",
            defaults["homepage"].get("homepageFaqIds", []),
        ),
        "bands": {
            **default_bands,
            **legacy_bands,
            "rooms": merge_band("rooms"),
            "experiences": merge_band("experiences"),
            "amenities": merge_band("amenities"),
            "gallery": merge_band("gallery"),
            "offers": merge_band("offers"),
            "testimonials": merge_band("testimonials"),
            "faqs": merge_band("faqs"),
            "location": merge_band("location"),
        },
    }

    rooms = []
    for room in raw.get("rooms", defaults["rooms"]):
        rooms.append(
            {
                **room,
                "tagline": room.get("tagline", ""),
                "priceFrom": room.get("priceFrom", 0),
            }
        )

    offers = [
        _normalize_offer(offer, index)
        for index, offer in enumerate(raw.get("offers", defaults["offers"]))
    ]

    testimonials = []
    for item in raw.get("testimonials", defaults["testimonials"]):
        testimonials.append(
            {
                **item,
                "guestLocation": item.get("guestLocation", ""),
                "initials": item.get("initials")
                or (item.get("guestName", "")[:2].upper()),
            }
        )

    return {
        "homepage": homepage,
        "about": _normalize_about(raw.get("about")),
        "rooms": rooms,
        "amenities": raw.get("amenities", deepcopy(defaults["amenities"])),
        "experiences": experiences,
        "galleryCategories": raw.get("galleryCategories", deepcopy(defaults["galleryCategories"])),
        "galleryImages": raw.get("galleryImages", deepcopy(defaults["galleryImages"])),
        "offersSection": {**defaults["offersSection"], **(raw.get("offersSection") or {})},
        "offers": offers,
        "testimonials": testimonials,
        "faqs": raw.get("faqs", deepcopy(defaults["faqs"])),
        "contact": {**defaults["contact"], **(raw.get("contact") or {})},
        "location": {**defaults["location"], **(raw.get("location") or {})},
        "social": {**defaults["social"], **(raw.get("social") or {})},
        "footer": _normalize_footer(raw.get("footer")),
    }


def _normalize_about(raw: dict | None) -> dict:
    defaults = default_cms_content()["about"]
    source = raw or {}
    merged = {**defaults, **source}

    default_pillars = defaults.get("pillars") or []
    raw_pillars = source.get("pillars") or []
    if raw_pillars:
        pillars = []
        for index, pillar in enumerate(raw_pillars):
            base = default_pillars[index % len(default_pillars)] if default_pillars else {}
            pillars.append(
                {
                    **base,
                    **pillar,
                    "id": pillar.get("id") or f"about-pillar-{index + 1}",
                }
            )
    else:
        pillars = deepcopy(default_pillars)

    default_mosaic = defaults.get("mosaic") or []
    raw_mosaic = source.get("mosaic") or []
    if raw_mosaic:
        mosaic = []
        for index, item in enumerate(raw_mosaic):
            base = default_mosaic[index % len(default_mosaic)] if default_mosaic else {}
            mosaic.append(
                {
                    **base,
                    **item,
                    "id": item.get("id") or f"about-mosaic-{index + 1}",
                }
            )
    else:
        mosaic = deepcopy(default_mosaic)

    for key in (
        "pageEyebrow",
        "lead",
        "storyEyebrow",
        "storyTitle",
        "storyHtml",
        "storyImageUrl",
        "pillarsEyebrow",
        "pillarsTitle",
        "atmosphereEyebrow",
        "atmosphereTitle",
        "atmosphereLead",
        "placeEyebrow",
        "placeTitle",
        "placeLead",
        "placeMeta",
        "placeCtaLabel",
        "placeDirectionsLabel",
        "placeImageUrl",
    ):
        if key not in source or source.get(key) in (None,):
            merged[key] = defaults.get(key, "")

    merged["pillars"] = pillars
    merged["mosaic"] = mosaic
    return merged
