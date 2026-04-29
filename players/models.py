"""
Players models — Player profile, stats, injuries, performance
"""
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Player(models.Model):
    class Status(models.TextChoices):
        ACTIVE   = "active",   _("Active")
        INJURED  = "injured",  _("Injured")
        SUSPENDED = "suspended", _("Suspended")
        RETIRED  = "retired",  _("Retired")
        TRANSFER = "transfer", _("Transfer Listed")

    class Foot(models.TextChoices):
        LEFT  = "left",  _("Left")
        RIGHT = "right", _("Right")
        BOTH  = "both",  _("Both")

    user         = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="player_profile",
    )
    full_name    = models.CharField(_("full name"), max_length=200)
    photo        = models.ImageField(upload_to="players/photos/", blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality  = models.CharField(max_length=100, blank=True)
    second_nationality = models.CharField(max_length=100, blank=True)
    position     = models.CharField(max_length=50, blank=True)
    secondary_position = models.CharField(max_length=50, blank=True)
    preferred_foot = models.CharField(max_length=10, choices=Foot.choices, default=Foot.RIGHT)
    height_cm    = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("Height (cm)"))
    weight_kg    = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("Weight (kg)"))
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    market_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    contract_until = models.DateField(null=True, blank=True)
    agent        = models.CharField(max_length=200, blank=True)
    bio          = models.TextField(blank=True)
    sport        = models.CharField(max_length=30, choices=settings.APEXFORGE_SPORT_CHOICES, default="football")
    jersey_number = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("player")
        verbose_name_plural = _("players")
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse("players:detail", kwargs={"pk": self.pk})

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        from django.utils import timezone
        today = timezone.now().date()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @property
    def current_team(self):
        roster = self.rosters.filter(is_active=True).select_related("team").first()
        return roster.team if roster else None


class PlayerStats(models.Model):
    """Season-level statistics per player per team."""
    player      = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="stats")
    team        = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="player_stats")
    season      = models.ForeignKey("teams.Season", on_delete=models.SET_NULL, null=True, blank=True)
    # Generic stats
    appearances = models.PositiveSmallIntegerField(default=0)
    starts      = models.PositiveSmallIntegerField(default=0)
    minutes     = models.PositiveIntegerField(default=0)
    goals       = models.PositiveSmallIntegerField(default=0)
    assists     = models.PositiveSmallIntegerField(default=0)
    yellow_cards = models.PositiveSmallIntegerField(default=0)
    red_cards   = models.PositiveSmallIntegerField(default=0)
    # Extended
    shots       = models.PositiveSmallIntegerField(default=0)
    shots_on_target = models.PositiveSmallIntegerField(default=0)
    passes      = models.PositiveIntegerField(default=0)
    pass_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tackles     = models.PositiveSmallIntegerField(default=0)
    interceptions = models.PositiveSmallIntegerField(default=0)
    rating      = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    notes       = models.TextField(blank=True)

    class Meta:
        verbose_name = _("player stats")
        verbose_name_plural = _("player stats")
        unique_together = [("player", "team", "season")]
        ordering = ["-season__start_date"]

    def __str__(self):
        return f"{self.player} — {self.team} — {self.season}"


class InjuryLog(models.Model):
    class Severity(models.TextChoices):
        MINOR    = "minor",    _("Minor")
        MODERATE = "moderate", _("Moderate")
        SEVERE   = "severe",   _("Severe")

    player       = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="injuries")
    injury_type  = models.CharField(max_length=200)
    body_part    = models.CharField(max_length=100, blank=True)
    severity     = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MINOR)
    injury_date  = models.DateField()
    expected_return = models.DateField(null=True, blank=True)
    actual_return = models.DateField(null=True, blank=True)
    treatment    = models.TextField(blank=True)
    notes        = models.TextField(blank=True)
    recorded_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="injury_records",
    )

    class Meta:
        verbose_name = _("injury log")
        verbose_name_plural = _("injury logs")
        ordering = ["-injury_date"]

    def __str__(self):
        return f"{self.player} — {self.injury_type} ({self.injury_date})"

    @property
    def is_active(self):
        return self.actual_return is None


class PerformanceMetric(models.Model):
    """Flexible key-value metric (speed, stamina, etc.) per player per date."""
    player     = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="metrics")
    metric     = models.CharField(max_length=100)  # e.g., "Sprint Speed"
    value      = models.DecimalField(max_digits=10, decimal_places=3)
    unit       = models.CharField(max_length=30, blank=True)  # e.g., "km/h"
    date       = models.DateField()
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    notes      = models.TextField(blank=True)

    class Meta:
        verbose_name = _("performance metric")
        verbose_name_plural = _("performance metrics")
        ordering = ["-date", "metric"]

    def __str__(self):
        return f"{self.player} — {self.metric}: {self.value}{self.unit} ({self.date})"
