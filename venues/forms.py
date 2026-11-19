from django import forms

from .models import Venue


class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ["name", "description", "address", "city", "capacity", "price_per_hour"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "capacity": forms.NumberInput(attrs={"class": "form-control"}),
            "price_per_hour": forms.NumberInput(attrs={"class": "form-control"}),
        }