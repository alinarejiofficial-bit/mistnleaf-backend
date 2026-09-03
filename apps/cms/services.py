"""CMS storage and publish filtering."""
from __future__ import annotations

import logging
import re
import time
from decimal import Decimal, InvalidOperation

from django.db import DatabaseError, OperationalError, transaction
from django.utils.html import strip_tags
from django.utils.text import slugify

from .defaults import default_cms_content
from .models import CmsContentStore, SINGLETON_PK
from .normalize import normalize_cms_content
from .published import filter_published_content

logger = logging.getLogger(__name__)

MAX_WRITE_RETRIES = 5

# Keep in sync with apps.website.cms_loader.ROOM_ID_SLUGS
ROOM_ID_SLUGS = {
    "cms-room-1": "canopy-suite",
    "cms-room-2": "mist-cottage",
    "cms-room-3": "leaf-room",
}


def cms_store_exists() -> bool:
    try:
        store = CmsContentStore.objects.filter(pk=SINGLETON_PK).first()
        return bool(store and store.content)
    except DatabaseError:
        return False


def read_cms_content() -> dict:
    try:
        store = CmsContentStore.objects.filter(pk=SINGLETON_PK).first()
        if not store or not store.content:
            return normalize_cms_content(default_cms_content())
        return normalize_cms_content(store.content)
    except DatabaseError as exc:
        logger.warning("CMS read failed, using defaults: %s", exc)
        return normalize_cms_content(default_cms_content())


def _room_slug_for_cms_item(room: dict) -> str:
    mapped = ROOM_ID_SLUGS.get(room.get("id", ""))
    if mapped:
        return mapped
    name = (room.get("name") or "room").strip()
    slug = slugify(name) or re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "room"


def sync_published_rooms_to_inventory(content: dict) -> None:
    """
    Mirror published CMS room pages into RoomType so the public site and
    booking flow see the same rooms the dashboard edits.
    """
    try:
        from apps.rooms.models import RoomType
    except Exception as exc:
        logger.warning("Room sync skipped (rooms app unavailable): %s", exc)
        return

    for room in content.get("rooms") or []:
        name = (room.get("name") or "").strip()
        if not name:
            continue

        status = room.get("status") or "Published"
        slug = _room_slug_for_cms_item(room)
        images = [
            img for img in (room.get("images") or []) if isinstance(img, str) and img.strip()
        ]
        image = images[0] if images else ""
        safe_image = (
            image if image.startswith(("http://", "https://", "/media/")) else ""
        )

        try:
            raw_price = room.get("priceFrom")
            rate = Decimal(str(raw_price if raw_price not in (None, "") else 0))
        except (InvalidOperation, TypeError, ValueError):
            rate = Decimal("0")

        defaults = {
            "name": name,
            "short_description": (room.get("tagline") or "")[:255],
            "description": strip_tags(room.get("description") or ""),
            "max_guests": max(int(room.get("capacity") or 2), 1),
            "base_rate": rate,
            "amenities": room.get("amenities") or [],
            "is_active": status == "Published",
        }
        if safe_image:
            defaults["image"] = safe_image[:500]
            defaults["gallery"] = images

        try:
            RoomType.objects.update_or_create(slug=slug, defaults=defaults)
        except Exception as exc:
            logger.warning("Failed to sync CMS room %s (%s): %s", room.get("id"), slug, exc)


def write_cms_content(content: dict, user=None) -> dict:
    normalized = normalize_cms_content(content)
    last_error: Exception | None = None

    for attempt in range(MAX_WRITE_RETRIES):
        try:
            with transaction.atomic():
                CmsContentStore.objects.update_or_create(
                    pk=SINGLETON_PK,
                    defaults={
                        "content": normalized,
                        "updated_by": user,
                    },
                )
            try:
                sync_published_rooms_to_inventory(normalized)
            except Exception as exc:
                logger.warning("CMS room inventory sync failed: %s", exc)
            return normalized
        except OperationalError as exc:
            last_error = exc
            if "locked" not in str(exc).lower() or attempt >= MAX_WRITE_RETRIES - 1:
                raise
            time.sleep(0.15 * (attempt + 1))

    if last_error:
        raise last_error
    return normalized


def read_published_cms_content() -> dict:
    return filter_published_content(read_cms_content())
