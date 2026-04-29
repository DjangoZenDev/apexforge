from django import forms
from .models import ClubBranding


class ClubBrandingForm(forms.ModelForm):
    class Meta:
        model = ClubBranding
        fields = [
            "name", "tagline", "logo", "primary_color", "secondary_color",
            "founded_year", "city", "country", "website", "email", "phone",
            "twitter", "instagram", "facebook", "youtube",
            "tiktok", "linkedin", "discord", "twitch", "description",
        ]
        widgets = {
            "name":           forms.TextInput(attrs={"class": "form-input"}),
            "tagline":        forms.TextInput(attrs={"class": "form-input"}),
            "logo":           forms.FileInput(attrs={"class": "form-input"}),
            "primary_color":  forms.TextInput(attrs={"class": "form-input", "type": "color"}),
            "secondary_color":forms.TextInput(attrs={"class": "form-input", "type": "color"}),
            "founded_year":   forms.NumberInput(attrs={"class": "form-input"}),
            "city":           forms.TextInput(attrs={"class": "form-input"}),
            "country":        forms.TextInput(attrs={"class": "form-input"}),
            "website":        forms.URLInput(attrs={"class": "form-input"}),
            "email":          forms.EmailInput(attrs={"class": "form-input"}),
            "phone":          forms.TextInput(attrs={"class": "form-input"}),
            "twitter":        forms.TextInput(attrs={"class": "form-input"}),
            "instagram":      forms.TextInput(attrs={"class": "form-input"}),
            "facebook":       forms.TextInput(attrs={"class": "form-input"}),
            "youtube":        forms.TextInput(attrs={"class": "form-input"}),
            "tiktok":         forms.TextInput(attrs={"class": "form-input"}),
            "linkedin":       forms.TextInput(attrs={"class": "form-input"}),
            "discord":        forms.TextInput(attrs={"class": "form-input"}),
            "twitch":         forms.TextInput(attrs={"class": "form-input"}),
            "description":    forms.Textarea(attrs={"class": "form-input", "rows": 4}),
        }
