from django import forms


class EnquiryForm(forms.Form):
    name = forms.CharField(
        min_length=2,
        max_length=120,
        widget=forms.TextInput(attrs={"autocomplete": "name", "placeholder": "Your name"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "you@email.com"}),
    )
    phone = forms.CharField(
        min_length=7,
        max_length=20,
        widget=forms.TextInput(attrs={"autocomplete": "tel", "placeholder": "+91 …"}),
    )
    subject = forms.ChoiceField(
        choices=[
            ("Stay enquiry", "Stay enquiry"),
            ("Availability question", "Availability question"),
            ("Directions/transfers", "Directions / transfers"),
            ("Experiences", "Experiences"),
            ("Other", "Other"),
        ]
    )
    message = forms.CharField(
        min_length=10,
        widget=forms.Textarea(
            attrs={"rows": 5, "placeholder": "Dates, guests, or anything we should know…"}
        ),
    )


class BookingSearchForm(forms.Form):
    check_in = forms.DateField(
        label="Check-in",
        widget=forms.DateInput(attrs={"type": "date", "class": "booking-field__input"}),
    )
    check_out = forms.DateField(
        label="Check-out",
        widget=forms.DateInput(attrs={"type": "date", "class": "booking-field__input"}),
    )
    guests = forms.IntegerField(
        min_value=1,
        max_value=6,
        initial=2,
        widget=forms.NumberInput(attrs={"class": "booking-field__input", "min": 1, "max": 6}),
    )
    room = forms.CharField(required=False, widget=forms.HiddenInput)
