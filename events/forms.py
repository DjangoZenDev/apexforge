from django import forms
from .models import Event, Fixture, Tournament


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title", "event_type", "status", "team", "opponent",
            "venue", "is_home", "start_date", "start_time",
            "end_date", "end_time", "description", "notes",
        ]
        widgets = {
            "title":       forms.TextInput(attrs={"class": "form-input"}),
            "event_type":  forms.Select(attrs={"class": "form-select"}),
            "status":      forms.Select(attrs={"class": "form-select"}),
            "team":        forms.Select(attrs={"class": "form-select"}),
            "opponent":    forms.TextInput(attrs={"class": "form-input"}),
            "venue":       forms.TextInput(attrs={"class": "form-input"}),
            "start_date":  forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "start_time":  forms.TimeInput(attrs={"class": "form-input", "type": "time"}),
            "end_date":    forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "end_time":    forms.TimeInput(attrs={"class": "form-input", "type": "time"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "notes":       forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }


class FixtureForm(forms.ModelForm):
    class Meta:
        model = Fixture
        exclude = ["event"]
        widgets = {
            "home_score":   forms.NumberInput(attrs={"class": "form-input"}),
            "away_score":   forms.NumberInput(attrs={"class": "form-input"}),
            "competition":  forms.TextInput(attrs={"class": "form-input"}),
            "referee":      forms.TextInput(attrs={"class": "form-input"}),
            "attendance":   forms.NumberInput(attrs={"class": "form-input"}),
            "match_report": forms.Textarea(attrs={"class": "form-input", "rows": 4}),
        }


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = "__all__"
        widgets = {
            "name":        forms.TextInput(attrs={"class": "form-input"}),
            "sport":       forms.Select(attrs={"class": "form-select"}),
            "start_date":  forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "end_date":    forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "location":    forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "teams":       forms.CheckboxSelectMultiple(),
            "organizer":   forms.TextInput(attrs={"class": "form-input"}),
            "prize_money": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
        }
