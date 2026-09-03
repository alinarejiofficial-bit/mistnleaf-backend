from django.core.management.base import BaseCommand

from apps.enquiries.models import Enquiry


class Command(BaseCommand):
    help = "Seed demo enquiries matching the admin dashboard samples."

    def handle(self, *args, **options):
        samples = [
            {
                "name": "Ritu Malhotra",
                "email": "ritu.m@email.com",
                "subject": "Family suite availability for Diwali",
                "channel": Enquiry.Channel.WEBSITE,
                "status": Enquiry.Status.NEW,
            },
            {
                "name": "Corporate Desk — NovaTech",
                "email": "travel@novatech.com",
                "subject": "Group booking for 12 rooms",
                "channel": Enquiry.Channel.EMAIL,
                "status": Enquiry.Status.IN_PROGRESS,
            },
            {
                "name": "Amit Joshi",
                "email": "amit.j@email.com",
                "subject": "Pet-friendly room enquiry",
                "channel": Enquiry.Channel.PHONE,
                "status": Enquiry.Status.CLOSED,
            },
            {
                "name": "Elena Rossi",
                "email": "elena.rossi@email.com",
                "subject": "Honeymoon package details",
                "channel": Enquiry.Channel.WEBSITE,
                "status": Enquiry.Status.NEW,
            },
        ]

        created = 0
        for item in samples:
            _, was_created = Enquiry.objects.get_or_create(
                email=item["email"],
                subject=item["subject"],
                defaults={
                    "name": item["name"],
                    "channel": item["channel"],
                    "status": item["status"],
                    "message": f"Demo enquiry: {item['subject']}",
                },
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded enquiries ({created} new)."))
