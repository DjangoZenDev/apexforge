from django import forms
from .models import Player, PlayerStats, InjuryLog, PerformanceMetric


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = [
            "full_name", "photo", "date_of_birth", "nationality", "second_nationality",
            "position", "secondary_position", "preferred_foot", "height_cm", "weight_kg",
            "status", "market_value", "contract_until", "agent", "bio",
            "sport", "jersey_number",
        ]
        widgets = {
            "full_name":    forms.TextInput(attrs={"class": "form-input"}),
            "photo":        forms.FileInput(attrs={"class": "form-input"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "nationality":  forms.TextInput(attrs={"class": "form-input"}),
            "second_nationality": forms.TextInput(attrs={"class": "form-input"}),
            "position":     forms.TextInput(attrs={"class": "form-input"}),
            "secondary_position": forms.TextInput(attrs={"class": "form-input"}),
            "preferred_foot": forms.Select(attrs={"class": "form-select"}),
            "height_cm":    forms.NumberInput(attrs={"class": "form-input"}),
            "weight_kg":    forms.NumberInput(attrs={"class": "form-input"}),
            "status":       forms.Select(attrs={"class": "form-select"}),
            "market_value": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "contract_until": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "agent":        forms.TextInput(attrs={"class": "form-input"}),
            "bio":          forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "sport":        forms.Select(attrs={"class": "form-select"}),
            "jersey_number": forms.NumberInput(attrs={"class": "form-input"}),
        }


class PlayerStatsForm(forms.ModelForm):
    class Meta:
        model = PlayerStats
        exclude = ["player"]
        widgets = {
            "team":      forms.Select(attrs={"class": "form-select"}),
            "season":    forms.Select(attrs={"class": "form-select"}),
            "rating":    forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0", "max": "10"}),
            "pass_accuracy": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "notes":     forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }


class InjuryLogForm(forms.ModelForm):
    class Meta:
        model = InjuryLog
        exclude = ["player", "recorded_by"]
        widgets = {
            "injury_type":   forms.TextInput(attrs={"class": "form-input"}),
            "body_part":     forms.TextInput(attrs={"class": "form-input"}),
            "severity":      forms.Select(attrs={"class": "form-select"}),
            "injury_date":   forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "expected_return": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "actual_return": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "treatment":     forms.Textarea(attrs={"class": "form-input", "rows": 2}),
            "notes":         forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }


class PerformanceMetricForm(forms.ModelForm):
    class Meta:
        model = PerformanceMetric
        exclude = ["player", "recorded_by"]
        widgets = {
            "metric": forms.TextInput(attrs={"class": "form-input"}),
            "value":  forms.NumberInput(attrs={"class": "form-input", "step": "0.001"}),
            "unit":   forms.TextInput(attrs={"class": "form-input"}),
            "date":   forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "notes":  forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }
