from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0002_booking_amount_booking_guest_email_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="payment_method",
            field=models.CharField(
                blank=True,
                choices=[
                    ("UPI", "UPI"),
                    ("Card", "Card"),
                    ("Cash", "Cash"),
                    ("Bank transfer", "Bank transfer"),
                ],
                default="",
                max_length=20,
            ),
        ),
    ]
