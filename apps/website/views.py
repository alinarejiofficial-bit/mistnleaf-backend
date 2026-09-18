from datetime import datetime

from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from apps.rooms.models import RoomType
from apps.website import booking_helpers as bh
from apps.website import cms_loader as cms
from apps.website.services import create_website_booking, create_website_enquiry
from apps.website.content import (
    DINING,
    MEDIA,
    NAV_LINKS,
    THINGS_TO_DO,
    format_inr,
)
from apps.website.forms import BookingSearchForm, EnquiryForm


def _ctx(**extra):
    return {
        "site": cms.get_cms_site(),
        "footer_cms": cms.get_cms_footer(),
        "social_cms": cms.get_cms_social(),
        "nav_links": NAV_LINKS,
        "media": MEDIA,
        "format_inr": format_inr,
        **extra,
    }


def _get_room_type_for_slug(slug: str) -> RoomType:
    room_type = RoomType.objects.filter(slug=slug, is_active=True).first()
    if not room_type:
        raise ValueError(f"Unknown room type slug: {slug}")
    return room_type


def home(request):
    bands = cms.get_cms_homepage_bands()
    show = cms.get_homepage_section_visibility()
    location = cms.get_cms_location()
    return render(
        request,
        "website/pages/home.html",
        _ctx(
            homepage=cms.get_cms_homepage(),
            about_band=cms.get_cms_about(),
            rooms=cms.featured_cms_rooms(3),
            rooms_band=bands["rooms"],
            experiences=cms.featured_cms_experiences(4),
            experiences_band=bands["experiences"],
            amenities=cms.featured_cms_amenities(3),
            amenities_band=bands["amenities"],
            gallery_images=cms.featured_cms_gallery(7),
            gallery_band=bands["gallery"],
            offers=cms.featured_cms_offers(3),
            offers_band=bands["offers"],
            testimonials=cms.featured_cms_testimonials(3),
            testimonials_band=bands["testimonials"],
            location_info=location,
            location_band=bands["location"],
            faqs=cms.featured_cms_faqs(4),
            faqs_band=bands["faqs"],
            show_sections=show,
        ),
    )


def about(request):
    about_cms = cms.get_cms_about()
    return render(
        request,
        "website/pages/about.html",
        _ctx(
            title=about_cms["title"] or "About Mistnleaf",
            about=about_cms,
        ),
    )


def rooms_list(request):
    rooms_band = cms.get_cms_homepage_bands()["rooms"]
    return render(
        request,
        "website/rooms/list.html",
        _ctx(
            title=rooms_band["title"] or "Rooms & Accommodation",
            eyebrow=rooms_band["eyebrow"] or "Stay",
            lead=rooms_band["lead"]
            or "Three carefully composed spaces — each with forest light, soft linens, and room to slow down.",
            rooms=cms.get_cms_rooms(),
        ),
    )


def room_detail(request, slug):
    room = cms.get_cms_room(slug)
    if not room:
        return redirect("website:rooms")
    return render(
        request,
        "website/rooms/detail.html",
        _ctx(title=room["name"], room=room),
    )


def experiences(request):
    band = cms.get_cms_homepage_bands()["experiences"]
    return render(
        request,
        "website/pages/grid.html",
        _ctx(
            title=band["title"] or "Experiences",
            eyebrow=band.get("eyebrow") or "Experiences",
            lead=band.get("lead") or "",
            items=cms.get_cms_experiences(),
        ),
    )


def amenities(request):
    band = cms.get_cms_homepage_bands()["amenities"]
    return render(
        request,
        "website/pages/grid.html",
        _ctx(
            title=band["title"] or "Amenities",
            eyebrow=band.get("eyebrow") or "Amenities",
            lead=band.get("lead") or "",
            items=cms.get_cms_amenities(),
        ),
    )


def gallery(request):
    band = cms.get_cms_homepage_bands()["gallery"]
    items = [
        {
            "title": item.get("label") or item.get("alt") or item.get("title") or "",
            "description": item.get("alt") or "",
            "image": item.get("src") or item.get("image") or "",
        }
        for item in cms.get_cms_gallery()
    ]
    return render(
        request,
        "website/pages/grid.html",
        _ctx(
            title=band["title"] or "Gallery",
            eyebrow=band.get("eyebrow") or "Gallery",
            lead=band.get("lead") or "",
            items=items,
        ),
    )


def offers(request):
    band = cms.get_cms_homepage_bands()["offers"]
    return render(
        request,
        "website/pages/offers.html",
        _ctx(
            title=band["title"] or "Offers & Packages",
            eyebrow=band.get("eyebrow") or "Packages",
            lead=band.get("lead")
            or "Thoughtful combinations of stay, meals, and experiences — without the clutter.",
            items=cms.get_cms_offers(),
        ),
    )


def dining(request):
    return render(request, "website/pages/dining.html", _ctx(title="Dining", dining=DINING))


def things_to_do(request):
    return render(
        request,
        "website/pages/grid.html",
        _ctx(
            title="Things to Do",
            eyebrow="Activities",
            lead="Day trips and nearby walks from the lodge — timed for mist, light, and quiet roads.",
            items=THINGS_TO_DO,
        ),
    )


def location(request):
    location_info = cms.get_cms_location()
    return render(
        request,
        "website/pages/location.html",
        _ctx(title=location_info["title"] or "Location", location_info=location_info),
    )


def faqs(request):
    band = cms.get_cms_homepage_bands()["faqs"]
    return render(
        request,
        "website/pages/faqs.html",
        _ctx(title=band["title"] or "FAQs", faqs=cms.get_cms_faqs()),
    )


def explore(request):
    return render(request, "website/pages/explore.html", _ctx(title="Explore the site"))


def contact(request):
    sent = request.GET.get("sent") == "1"
    form = EnquiryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        create_website_enquiry(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            subject=data["subject"],
            message=data["message"],
        )
        return redirect(f"{reverse('website:contact')}?sent=1")
    return render(
        request,
        "website/pages/contact.html",
        _ctx(
            title="Contact & Enquiries",
            form=form,
            sent=sent,
            missing=request.GET.get("error") == "missing",
            contact_info=cms.get_cms_contact(),
        ),
    )


def privacy(request):
    return render(
        request,
        "website/pages/legal.html",
        _ctx(title="Privacy Policy", lead="How Mistnleaf collects, uses, and protects information."),
    )


def terms(request):
    return render(
        request,
        "website/pages/legal.html",
        _ctx(title="Terms & Conditions", lead="Terms governing use of our website and services."),
    )


def cancellation(request):
    return render(
        request,
        "website/pages/legal.html",
        _ctx(title="Cancellation Policy", lead="How to modify or cancel your reservation."),
    )


def booking_entry(request):
    return redirect("website:booking_search")


@require_http_methods(["GET", "POST"])
def booking_search(request):
    query = bh.parse_booking_query(request.GET)
    form = BookingSearchForm(
        request.POST or None,
        initial={
            "check_in": query["check_in"] or None,
            "check_out": query["check_out"] or None,
            "guests": query["guests"] or 2,
            "room": query["room"],
        },
    )
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        if data["check_out"] < data["check_in"]:
            return render(
                request,
                "website/booking/search.html",
                _ctx(
                    form=form,
                    query=query,
                    booking_steps=bh.booking_progress("search"),
            current_step="search",
                    error="dates",
                ),
            )
        params = bh.booking_query_string(
            {},
            {
                "check_in": data["check_in"].isoformat(),
                "check_out": data["check_out"].isoformat(),
                "guests": str(data["guests"]),
                "room": data.get("room") or "",
            },
        )
        return redirect(f"{reverse('website:booking_availability')}?{params}")
    return render(
        request,
        "website/booking/search.html",
        _ctx(form=form, query=query, booking_steps=bh.booking_progress("search"),
            current_step="search"),
    )


def booking_availability(request):
    query = bh.parse_booking_query(request.GET)
    if not bh.require_search(query):
        return redirect("website:booking_search")
    guests = int(query["guests"])
    availability = bh.get_booking_availability(query["check_in"], query["check_out"], guests)
    open_count = sum(1 for item in availability if item["available"])
    availability_lead = (
        f"{open_count} room type{'s' if open_count != 1 else ''} open for "
        f"{bh.format_stay_range(query['check_in'], query['check_out'])}."
    )
    return render(
        request,
        "website/booking/availability.html",
        _ctx(
            query=query,
            q=bh.booking_query_string(query),
            booking_steps=bh.booking_progress("availability"),
            current_step="availability",
            availability=availability,
            open_count=open_count,
            lead=availability_lead,
        ),
    )


@require_http_methods(["GET", "POST"])
def booking_select(request):
    query = bh.parse_booking_query(request.POST if request.method == "POST" else request.GET)
    if not bh.require_search(query):
        return redirect("website:booking_search")
    availability = bh.get_booking_availability(
        query["check_in"], query["check_out"], int(query["guests"])
    )
    if request.method == "POST":
        slug = request.POST.get("room")
        match = next(
            (item for item in availability if item["room"]["slug"] == slug and item["available"]),
            None,
        )
        if not match:
            params = bh.booking_query_string(query)
            return redirect(f"{reverse('website:booking_availability')}?{params}&error=unavailable")
        query["room"] = slug
        return redirect(f"{reverse('website:booking_guest')}?{bh.booking_query_string(query)}")
    return render(
        request,
        "website/booking/select.html",
        _ctx(
            query=query,
            q=bh.booking_query_string(query),
            booking_steps=bh.booking_progress("select"),
            current_step="select",
            availability=[i for i in availability if i["available"]],
        ),
    )


def booking_guest(request):
    query = bh.parse_booking_query(request.POST if request.method == "POST" else request.GET)
    if not query.get("room") or not cms.get_cms_room(query["room"]):
        return redirect("website:booking_search")
    if request.method == "POST":
        if query.get("name") and query.get("email"):
            return redirect(f"{reverse('website:booking_summary')}?{bh.booking_query_string(query)}")
    room = cms.get_cms_room(query["room"])
    return render(
        request,
        "website/booking/guest.html",
        _ctx(
            query=query,
            q=bh.booking_query_string(query),
            booking_steps=bh.booking_progress("guest"),
            current_step="guest",
            room=room,
        ),
    )


def booking_summary(request):
    query = bh.parse_booking_query(request.GET)
    room = cms.get_cms_room(query.get("room", ""))
    if not room or not query.get("name"):
        return redirect("website:booking_search")
    nights = bh.nights_between(query["check_in"], query["check_out"])
    subtotal = room["price"] * nights
    taxes = round(subtotal * 0.12)
    total = subtotal + taxes
    return render(
        request,
        "website/booking/summary.html",
        _ctx(
            query=query,
            q=bh.booking_query_string(query),
            booking_steps=bh.booking_progress("summary"),
            current_step="summary",
            room=room,
            nights=nights,
            subtotal=subtotal,
            taxes=taxes,
            total=total,
        ),
    )


def booking_payment(request):
    query = bh.parse_booking_query(request.GET)
    room = cms.get_cms_room(query.get("room", ""))
    booking_ref = query.get("ref")
    booking_error = None

    if room and query.get("name") and query.get("email") and query.get("check_in") and query.get("check_out"):
        if not booking_ref:
            try:
                check_in = datetime.strptime(query["check_in"], "%Y-%m-%d").date()
                check_out = datetime.strptime(query["check_out"], "%Y-%m-%d").date()
                nights = bh.nights_between(query["check_in"], query["check_out"])
                amount = room["price"] * nights
                booking = create_website_booking(
                    guest_name=query["name"],
                    guest_email=query["email"],
                    guest_phone=query.get("phone") or "",
                    room_type=_get_room_type_for_slug(room["slug"]),
                    check_in=check_in,
                    check_out=check_out,
                    adults=int(query.get("guests") or 2),
                    children=0,
                    amount=amount,
                    notes=query.get("notes") or "",
                )
                booking_ref = booking.reference
            except Exception:
                booking_error = "Unable to create booking request. Please try again or contact us."

    return render(
        request,
        "website/booking/payment.html",
        _ctx(
            query=query,
            booking_steps=bh.booking_progress("payment"),
            current_step="payment",
            booking_ref=booking_ref,
            booking_error=booking_error,
            message="Online payment integration will connect to the bookings API in the next step.",
        ),
    )


def booking_confirmation(request):
    return render(
        request,
        "website/booking/confirmation.html",
        _ctx(
            query=bh.parse_booking_query(request.GET),
            booking_steps=bh.booking_progress("confirmation"),
            current_step="confirmation",
        ),
    )
