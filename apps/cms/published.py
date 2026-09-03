"""Filter published CMS sections — mirrors mistnleaf_admin/src/lib/cms-published.ts"""
from __future__ import annotations

from datetime import datetime, timezone


def _is_published(status: str | None) -> bool:
    return status == "Published"


def filter_published_content(content: dict) -> dict:
    def section(key: str):
        item = content[key]
        if _is_published(item.get("status")):
            return item
        return {**item, "status": "Draft"}

    return {
        "homepage": section("homepage"),
        "about": section("about"),
        "rooms": [r for r in content.get("rooms", []) if _is_published(r.get("status"))],
        "amenities": [a for a in content.get("amenities", []) if _is_published(a.get("status"))],
        "experiences": [e for e in content.get("experiences", []) if _is_published(e.get("status"))],
        "galleryCategories": [
            c for c in content.get("galleryCategories", []) if _is_published(c.get("status"))
        ],
        "galleryImages": [
            i for i in content.get("galleryImages", []) if _is_published(i.get("status"))
        ],
        "offers": [
            o
            for o in content.get("offers", [])
            if _is_published(o.get("status")) and o.get("active", True)
        ],
        "offersSection": section("offersSection"),
        "testimonials": [
            t for t in content.get("testimonials", []) if _is_published(t.get("status"))
        ],
        "faqs": [f for f in content.get("faqs", []) if _is_published(f.get("status"))],
        "contact": section("contact"),
        "location": section("location"),
        "social": section("social"),
        "footer": section("footer"),
        "publishedAt": datetime.now(timezone.utc).isoformat(),
    }
