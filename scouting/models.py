"""
Scouting models — reports, talent database, watchlist
"""
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class ScoutReport(models.Model):
    class Recommendation(models.TextChoices):
        SIGN_NOW     = "sign_now",     _("Sign Now")
        MONITOR      = "monitor",      _("Monitor")
        TRIAL        = "trial",        _("Invite for Trial")
        NOT_SUITABLE = "not_suitable", _("Not Suitable")

    player      = models.ForeignKey(
        "players.Player", on_delete=models.CASCADE, related_name="scout_reports",
    )
    scout       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="scout_reports",
    )
    match_date  = models.DateField()
    venue       = models.CharField(max_length=200, blank=True)
    opponent    = models.CharField(max_length=200, blank=True)

    # Rating categories 1-10
    technical   = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], default=5,
    )
    tactical    = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], default=5,
    )
    physical    = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], default=5,
    )
    mental      = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], default=5,
    )
    overall     = models.DecimalField(
        max_digits=4, decimal_places=2,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    strengths   = models.TextField(blank=True)
    weaknesses  = models.TextField(blank=True)
    summary     = models.TextField()
    recommendation = models.CharField(max_length=20, choices=Recommendation.choices)
    attachment  = models.FileField(upload_to="scouting/reports/", blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("scout report")
        verbose_name_plural = _("scout reports")
        ordering = ["-match_date"]

    def __str__(self):
        return f"Report: {self.player} — {self.match_date}"

    def get_absolute_url(self):
        return reverse("scouting:report_detail", kwargs={"pk": self.pk})


class TalentProfile(models.Model):
    """Potential recruit not yet in the player database."""
    class Status(models.TextChoices):
        PROSPECT  = "prospect",  _("Prospect")
        CONTACTED = "contacted", _("Contacted")
        TRIALING  = "trialing",  _("On Trial")
        SIGNED    = "signed",    _("Signed")
        REJECTED  = "rejected",  _("Rejected")

    full_name    = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality  = models.CharField(max_length=100, blank=True)
    position     = models.CharField(max_length=50, blank=True)
    current_club = models.CharField(max_length=200, blank=True)
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.PROSPECT)
    rating       = models.PositiveSmallIntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    notes        = models.TextField(blank=True)
    contact_info = models.TextField(blank=True)
    video_url    = models.URLField(blank=True)
    photo        = models.ImageField(upload_to="scouting/talents/", blank=True, null=True)
    added_by     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="added_talents",
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("talent profile")
        verbose_name_plural = _("talent profiles")
        ordering = ["-rating", "full_name"]

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse("scouting:talent_detail", kwargs={"pk": self.pk})


class Watchlist(models.Model):
    """A named watchlist per scout/manager."""
    name    = models.CharField(max_length=100)
    owner   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watchlists",
    )
    players = models.ManyToManyField("players.Player", blank=True, related_name="watchlists")
    talents = models.ManyToManyField(TalentProfile, blank=True, related_name="watchlists")
    notes   = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("watchlist")
        unique_together = [("owner", "name")]

    def __str__(self):
        return f"{self.owner} — {self.name}"
