from django import forms
from django.utils.translation import gettext_lazy as _
from .models import AcademyProgram, DevelopmentPlan, DevelopmentMilestone


class AcademyProgramForm(forms.ModelForm):
    class Meta:
        model = AcademyProgram
        fields = ["name", "age_group", "description", "head_coach", "team",
                  "start_date", "end_date", "max_players", "is_active", "goals"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "goals": forms.Textarea(attrs={"rows": 3}),
        }


class DevelopmentPlanForm(forms.ModelForm):
    class Meta:
        model = DevelopmentPlan
        fields = ["player", "season", "goals", "strengths", "areas_to_improve",
                  "technical_rating", "tactical_rating", "physical_rating",
                  "mental_rating", "overall_rating", "coach_notes"]
        widgets = {
            "goals": forms.Textarea(attrs={"rows": 3}),
            "strengths": forms.Textarea(attrs={"rows": 2}),
            "areas_to_improve": forms.Textarea(attrs={"rows": 2}),
            "coach_notes": forms.Textarea(attrs={"rows": 3}),
            "technical_rating": forms.NumberInput(attrs={"min": 1, "max": 10}),
            "tactical_rating": forms.NumberInput(attrs={"min": 1, "max": 10}),
            "physical_rating": forms.NumberInput(attrs={"min": 1, "max": 10}),
            "mental_rating": forms.NumberInput(attrs={"min": 1, "max": 10}),
            "overall_rating": forms.NumberInput(attrs={"min": 1, "max": 10}),
        }


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = DevelopmentMilestone
        fields = ["title", "description", "target_date", "notes"]
        widgets = {
            "target_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 2}),
        }
