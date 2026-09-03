"""Load default CMS JSON bundled with the app."""
from __future__ import annotations

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "default_cms_content.json"


def default_cms_content() -> dict:
    if DATA_FILE.exists():
        with DATA_FILE.open(encoding="utf-8") as handle:
            return json.load(handle)
    return {
        "homepage": {"status": "Published", "heroHeadline": "Mistnleaf"},
        "about": {"status": "Published"},
        "rooms": [],
        "amenities": [],
        "experiences": [],
        "galleryCategories": [],
        "galleryImages": [],
        "offersSection": {"status": "Published"},
        "offers": [],
        "testimonials": [],
        "faqs": [],
        "contact": {"status": "Published"},
        "location": {"status": "Published"},
        "social": {"status": "Published"},
        "footer": {"status": "Published"},
    }
