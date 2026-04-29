from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Injury, RecoveryPlan, Treatment, MedicalRecord


class InjuryForm(forms.ModelForm):
    class Meta:
        model = Injury
        fields = ["player", "injury_type", "body_part", "severity", "status",
                  "injury_date", "expected_recovery", "actual_recovery", "mechanism", "description"]
        widgets = {
            "injury_date": forms.DateInput(attrs={"type": "date"}),
            "expected_recovery": forms.DateInput(attrs={"type": "date"}),
            "actual_recovery": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "mechanism": forms.TextInput(),
        }


class RecoveryPlanForm(forms.ModelForm):
    class Meta:
        model = RecoveryPlan
        fields = ["plan_details", "start_date", "target_date", "physio_name", "milestones", "progress_notes"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "target_date": forms.DateInput(attrs={"type": "date"}),
            "plan_details": forms.Textarea(attrs={"rows": 4}),
            "milestones": forms.Textarea(attrs={"rows": 4, "placeholder": "One milestone per line"}),
            "progress_notes": forms.Textarea(attrs={"rows": 3}),
        }


class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
        fields = ["treatment_type", "date", "practitioner", "notes", "next_session"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "next_session": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ["record_type", "date", "description", "physician", "facility", "file", "is_confidential"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }
