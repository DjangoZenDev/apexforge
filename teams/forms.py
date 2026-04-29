from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Team, Roster, Season, Division


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            "name", "short_name", "sport", "division", "season", "logo",
            "home_venue", "city", "country", "founded_year",
            "manager", "coach", "status", "description", "colors", "website",
        ]
        widgets = {
            "name":         forms.TextInput(attrs={"class": "form-input"}),
            "short_name":   forms.TextInput(attrs={"class": "form-input"}),
            "sport":        forms.Select(attrs={"class": "form-select"}),
            "division":     forms.Select(attrs={"class": "form-select"}),
            "season":       forms.Select(attrs={"class": "form-select"}),
            "logo":         forms.FileInput(attrs={"class": "form-input"}),
            "home_venue":   forms.TextInput(attrs={"class": "form-input"}),
            "city":         forms.TextInput(attrs={"class": "form-input"}),
            "country":      forms.TextInput(attrs={"class": "form-input"}),
            "founded_year": forms.NumberInput(attrs={"class": "form-input"}),
            "manager":      forms.Select(attrs={"class": "form-select"}),
            "coach":        forms.Select(attrs={"class": "form-select"}),
            "status":       forms.Select(attrs={"class": "form-select"}),
            "description":  forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "colors":       forms.TextInput(attrs={"class": "form-input", "placeholder": "e.g. Green/White"}),
            "website":      forms.URLInput(attrs={"class": "form-input"}),
        }


POSITION_CHOICES = [
    ("", _("— Select position —")),
    # Goalkeepers
    ("Goalkeeper",          _("Goalkeeper")),
    # Defenders
    ("Centre Back",         _("Centre Back")),
    ("Right Back",          _("Right Back")),
    ("Left Back",           _("Left Back")),
    ("Right Wing-Back",     _("Right Wing-Back")),
    ("Left Wing-Back",      _("Left Wing-Back")),
    ("Sweeper",             _("Sweeper")),
    # Midfielders
    ("Defensive Midfielder",  _("Defensive Midfielder")),
    ("Central Midfielder",    _("Central Midfielder")),
    ("Attacking Midfielder",  _("Attacking Midfielder")),
    ("Right Midfielder",      _("Right Midfielder")),
    ("Left Midfielder",       _("Left Midfielder")),
    ("Box-to-Box Midfielder", _("Box-to-Box Midfielder")),
    # Forwards / Wingers
    ("Right Winger",        _("Right Winger")),
    ("Left Winger",         _("Left Winger")),
    ("Centre Forward",      _("Centre Forward")),
    ("Striker",             _("Striker")),
    ("Second Striker",      _("Second Striker")),
    # Other sports
    ("Point Guard",         _("Point Guard")),
    ("Shooting Guard",      _("Shooting Guard")),
    ("Small Forward",       _("Small Forward")),
    ("Power Forward",       _("Power Forward")),
    ("Center",              _("Center")),
    ("Other",               _("Other")),
]


class RosterForm(forms.ModelForm):
    position = forms.ChoiceField(
        choices=POSITION_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Roster
        fields = ["player", "season", "jersey_number", "position", "is_captain", "joined_date", "notes"]
        widgets = {
            "player":        forms.Select(attrs={"class": "form-select"}),
            "season":        forms.Select(attrs={"class": "form-select"}),
            "jersey_number": forms.NumberInput(attrs={"class": "form-input", "placeholder": "e.g. 9"}),
            "joined_date":   forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "notes":         forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-select the current season
        current = Season.objects.filter(is_current=True).first()
        if current and not self.initial.get("season") and not self.data.get("season"):
            self.fields["season"].initial = current.pk
        self.fields["season"].empty_label = _("— Select season —")
        self.fields["player"].empty_label = _("— Select player —")


class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ["name", "start_date", "end_date", "is_current"]
        widgets = {
            "name":       forms.TextInput(attrs={"class": "form-input"}),
            "start_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "end_date":   forms.DateInput(attrs={"class": "form-input", "type": "date"}),
        }


class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = ["name", "level", "sport"]
        widgets = {
            "name":  forms.TextInput(attrs={"class": "form-input"}),
            "level": forms.NumberInput(attrs={"class": "form-input"}),
            "sport": forms.Select(attrs={"class": "form-select"}),
        }
