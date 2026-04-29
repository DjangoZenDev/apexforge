"""
Teams models — Team, Season, Division, Roster
"""
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Season(models.Model):
    name       = models.CharField(max_length=100)  # e.g., "2024/25"
    start_date = models.DateField()
    end_date   = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("season")
        ordering = ["-start_date"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            Season.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class Division(models.Model):
    name  = models.CharField(max_length=100)
    level = models.PositiveSmallIntegerField(default=1)
    sport = models.CharField(max_length=30, choices=settings.APEXFORGE_SPORT_CHOICES, default="football")

    class Meta:
        verbose_name = _("division")
        ordering = ["level", "name"]

    def __str__(self):
        return self.name


class Team(models.Model):
    class Status(models.TextChoices):
        ACTIVE   = "active",   _("Active")
        INACTIVE = "inactive", _("Inactive")
        DISBANDED = "disbanded", _("Disbanded")

    club        = models.ForeignKey(
        "organizations.Club",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="teams",
        verbose_name=_("club"),
    )
    name        = models.CharField(_("team name"), max_length=200)
    short_name  = models.CharField(max_length=10, blank=True)
    sport       = models.CharField(max_length=30, choices=settings.APEXFORGE_SPORT_CHOICES, default="football")
    division    = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True, related_name="teams")
    season      = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name="teams")
    logo        = models.ImageField(upload_to="teams/logos/", blank=True, null=True)
    home_venue  = models.CharField(max_length=200, blank=True)
    city        = models.CharField(max_length=100, blank=True)
    country     = models.CharField(max_length=100, blank=True)
    founded_year = models.PositiveSmallIntegerField(null=True, blank=True)
    manager     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="managed_teams",
    )
    coach       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="coached_teams",
    )
    status      = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    description = models.TextField(blank=True)
    colors      = models.CharField(max_length=100, blank=True, help_text=_("Primary / secondary colors"))
    website     = models.URLField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("team")
        verbose_name_plural = _("teams")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("teams:detail", kwargs={"pk": self.pk})

    @property
    def player_count(self):
        return self.rosters.filter(is_active=True).count()


class Roster(models.Model):
    """A player's membership on a team for a given season."""
    team        = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="rosters")
    player      = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="rosters")
    season      = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True)
    jersey_number = models.PositiveSmallIntegerField(null=True, blank=True)
    position    = models.CharField(max_length=50, blank=True)
    is_captain  = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    joined_date = models.DateField(null=True, blank=True)
    left_date   = models.DateField(null=True, blank=True)
    notes       = models.TextField(blank=True)

    class Meta:
        verbose_name = _("roster entry")
        verbose_name_plural = _("roster entries")
        unique_together = [("team", "player", "season")]
        ordering = ["jersey_number", "player__full_name"]

    def __str__(self):
        return f"{self.player} — {self.team} (#{self.jersey_number})"
