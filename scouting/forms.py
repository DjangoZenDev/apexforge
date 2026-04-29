from django import forms
from .models import ScoutReport, TalentProfile, Watchlist


class ScoutReportForm(forms.ModelForm):
    class Meta:
        model = ScoutReport
        exclude = ["scout", "overall"]
        widgets = {
            "player":        forms.Select(attrs={"class": "form-select"}),
            "match_date":    forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "venue":         forms.TextInput(attrs={"class": "form-input"}),
            "opponent":      forms.TextInput(attrs={"class": "form-input"}),
            "technical":     forms.NumberInput(attrs={"class": "form-input", "min": 1, "max": 10}),
            "tactical":      forms.NumberInput(attrs={"class": "form-input", "min": 1, "max": 10}),
            "physical":      forms.NumberInput(attrs={"class": "form-input", "min": 1, "max": 10}),
            "mental":        forms.NumberInput(attrs={"class": "form-input", "min": 1, "max": 10}),
            "strengths":     forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "weaknesses":    forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "summary":       forms.Textarea(attrs={"class": "form-input", "rows": 4}),
            "recommendation": forms.Select(attrs={"class": "form-select"}),
            "attachment":    forms.FileInput(attrs={"class": "form-input"}),
        }


class TalentProfileForm(forms.ModelForm):
    class Meta:
        model = TalentProfile
        exclude = ["added_by"]
        widgets = {
            "full_name":    forms.TextInput(attrs={"class": "form-input"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "nationality":  forms.TextInput(attrs={"class": "form-input"}),
            "position":     forms.TextInput(attrs={"class": "form-input"}),
            "current_club": forms.TextInput(attrs={"class": "form-input"}),
            "status":       forms.Select(attrs={"class": "form-select"}),
            "rating":       forms.NumberInput(attrs={"class": "form-input", "min": 1, "max": 10}),
            "notes":        forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "contact_info": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
            "video_url":    forms.URLInput(attrs={"class": "form-input"}),
            "photo":        forms.FileInput(attrs={"class": "form-input"}),
        }


class WatchlistForm(forms.ModelForm):
    class Meta:
        model = Watchlist
        fields = ["name", "notes"]
        widgets = {
            "name":  forms.TextInput(attrs={"class": "form-input"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }
