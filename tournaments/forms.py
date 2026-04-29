from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Competition, Match


class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ["name", "slug", "sport", "competition_type", "status", "season",
                  "teams", "start_date", "end_date", "description", "logo", "prize_pool"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "teams": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False

    def clean_slug(self):
        from django.utils.text import slugify
        slug = self.cleaned_data.get("slug") or slugify(self.cleaned_data.get("name", ""))
        return slug


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ["stage", "group", "home_team", "away_team", "date", "venue",
                  "home_score", "away_score", "status", "round_number", "notes"]
        widgets = {
            "date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, competition=None, **kwargs):
        super().__init__(*args, **kwargs)
        if competition:
            self.fields["home_team"].queryset = competition.teams.all()
            self.fields["away_team"].queryset = competition.teams.all()
            self.fields["stage"].queryset = competition.stages.all()
            self.fields["group"].queryset = competition.stages.filter(
                stage_type="group"
            ).prefetch_related("groups").first().groups.all() if competition.stages.filter(
                stage_type="group").exists() else self.fields["group"].queryset.none()
        self.fields["stage"].required = False
        self.fields["group"].required = False
        self.fields["round_number"].required = False
        self.fields["home_score"].required = False
        self.fields["away_score"].required = False


class StandingForm(forms.Form):
    pass  # standings are auto-calculated
