from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

DEMO_USERS = [
    {
        "email": "admin@mistnleaf.com",
        "password": "Admin@123",
        "username": "admin",
        "first_name": "Priya",
        "last_name": "Sharma",
        "phone": "+91 98765 43210",
        "role": User.Role.SUPER_ADMINISTRATOR,
        "department": "Administration",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "email": "neha@mistnleaf.com",
        "password": "Staff@123",
        "username": "neha",
        "first_name": "Neha",
        "last_name": "Kapoor",
        "phone": "+91 98765 43211",
        "role": User.Role.RESORT_MANAGER,
        "department": "Management",
        "is_staff": True,
    },
    {
        "email": "arjun@mistnleaf.com",
        "password": "Staff@123",
        "username": "arjun",
        "first_name": "Arjun",
        "last_name": "Patel",
        "phone": "+91 98765 43212",
        "role": User.Role.FRONT_DESK,
        "department": "Front Office",
        "is_staff": True,
    },
    {
        "email": "sofia@mistnleaf.com",
        "password": "Staff@123",
        "username": "sofia",
        "first_name": "Sofia",
        "last_name": "Fernandes",
        "phone": "+91 98765 43213",
        "role": User.Role.HOUSEKEEPING,
        "department": "Housekeeping",
        "is_staff": True,
    },
    {
        "email": "ravi@mistnleaf.com",
        "password": "Staff@123",
        "username": "ravi",
        "first_name": "Ravi",
        "last_name": "Kumar",
        "phone": "+91 98765 43216",
        "role": User.Role.HOUSEKEEPING,
        "department": "Housekeeping",
        "is_staff": True,
    },
    {
        "email": "kavya@mistnleaf.com",
        "password": "Staff@123",
        "username": "kavya",
        "first_name": "Kavya",
        "last_name": "Nair",
        "phone": "+91 98765 43214",
        "role": User.Role.ACCOUNTANT,
        "department": "Finance",
        "is_staff": True,
    },
    {
        "email": "ishaan@mistnleaf.com",
        "password": "Staff@123",
        "username": "ishaan",
        "first_name": "Ishaan",
        "last_name": "Mehta",
        "phone": "+91 98765 43215",
        "role": User.Role.WEBSITE_CONTENT_MANAGER,
        "department": "Marketing",
        "is_staff": True,
    },
    # Public frontend /staff console demo accounts
    {
        "email": "manager@mistnleaf.demo",
        "password": "manager123",
        "username": "manager",
        "first_name": "Asha",
        "last_name": "Menon",
        "role": User.Role.RESORT_MANAGER,
        "department": "Management",
        "is_staff": True,
    },
    {
        "email": "frontdesk@mistnleaf.demo",
        "password": "desk123",
        "username": "frontdesk",
        "first_name": "Rahul",
        "last_name": "Iyer",
        "role": User.Role.FRONT_DESK,
        "department": "Front Office",
        "is_staff": True,
    },
]


class Command(BaseCommand):
    help = "Seed demo staff users matching the Mistnleaf frontend demo accounts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-passwords",
            action="store_true",
            help="Reset passwords for existing demo accounts.",
        )

    def handle(self, *args, **options):
        reset_passwords = options["reset_passwords"]
        created = 0
        updated = 0

        for data in DEMO_USERS:
            password = data.pop("password")
            email = data["email"]
            user, was_created = User.objects.get_or_create(email=email, defaults=data)

            if was_created:
                user.set_password(password)
                user.save()
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created {email}"))
                continue

            if reset_passwords:
                for field, value in data.items():
                    setattr(user, field, value)
                user.set_password(password)
                user.save()
                updated += 1
                self.stdout.write(self.style.WARNING(f"Updated {email}"))
            else:
                self.stdout.write(f"Skipped existing {email}")

        self.stdout.write(
            self.style.SUCCESS(f"Done. Created: {created}, Updated: {updated}")
        )
