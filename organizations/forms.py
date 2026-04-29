from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Organization, Club, UserClubAccess


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["name", "logo", "country", "website", "contact_email", "description", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = [
            "organization", "name", "city", "country", "stadium", "stadium_capacity",
            "founded_year", "contact_email", "phone", "logo", "colors", "website", "is_active",
        ]


class ClubAccessForm(forms.ModelForm):
    class Meta:
        model = UserClubAccess
        fields = ["user", "role", "is_primary"]
