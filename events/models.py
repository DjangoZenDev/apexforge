"""
Events models — fixtures, training, tournaments, attendance
"""
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Event(models.Model):
    class Type(models.TextChoices):
        FIXTURE    = "fixture",    _("Fixture / Match")
        TRAINING   = "training",   _("Training Session")
        TOURNAMENT = "tournament", _("Tournament")
        MEETING    = "meeting",    _("Meeting")
        OTHER      = "other",      _("Other")

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", _("Scheduled")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")
        POSTPONED = "postponed", _("Postponed")

    title        = models.CharField(max_length=200)
    event_type   = models.CharField(max_length=20, choices=Type.choices, default=Type.FIXTURE)
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    team         = models.ForeignKey(
        "teams.Team", on_delete=models.CASCADE, related_name="events", null=True, blank=True,
    )
    opponent     = models.CharField(max_length=200, blank=True)
    venue        = models.CharField(max_length=200, blank=True)
    is_home      = models.BooleanField(default=True)
    start_date   = models.DateField()
    start_time   = models.TimeField(null=True, blank=True)
    end_date     = models.DateField(null=True, blank=True)
    end_time     = models.TimeField(null=True, blank=True)
    description  = models.TextField(blank=True)
    notes        = models.TextField(blank=True)
    created_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="created_events",
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")
        ordering = ["start_date", "start_time"]

    def __str__(self):
        return f"{self.title} ({self.start_date})"

    def get_absolute_url(self):
        return reverse("events:detail", kwargs={"pk": self.pk})


class Fixture(models.Model):
    """Extra data for match-type events."""
    event        = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="fixture")
    home_score   = models.PositiveSmallIntegerField(null=True, blank=True)
    away_score   = models.PositiveSmallIntegerField(null=True, blank=True)
    competition  = models.CharField(max_length=200, blank=True)
    referee      = models.CharField(max_length=100, blank=True)
    attendance   = models.PositiveIntegerField(null=True, blank=True)
    match_report = models.TextField(blank=True)

    class Meta:
        verbose_name = _("fixture")

    def __str__(self):
        return f"{self.event} — {self.score}"

    @property
    def score(self):
        if self.home_score is not None and self.away_score is not None:
            return f"{self.home_score}–{self.away_score}"
        return "–"

    @property
    def result(self):
        if self.home_score is None or self.away_score is None:
            return None
        if self.home_score > self.away_score:
            return "W" if self.event.is_home else "L"
        elif self.home_score < self.away_score:
            return "L" if self.event.is_home else "W"
        return "D"


class Tournament(models.Model):
    name        = models.CharField(max_length=200)
    sport       = models.CharField(max_length=30, choices=settings.APEXFORGE_SPORT_CHOICES, default="football")
    start_date  = models.DateField()
    end_date    = models.DateField()
    location    = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    teams       = models.ManyToManyField("teams.Team", blank=True, related_name="tournaments")
    organizer   = models.CharField(max_length=200, blank=True)
    prize_money = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = _("tournament")
        ordering = ["-start_date"]

    def __str__(self):
        return self.name


class EventAttendance(models.Model):
    class AttendanceStatus(models.TextChoices):
        CONFIRMED = "confirmed", _("Confirmed")
        DECLINED  = "declined",  _("Declined")
        PENDING   = "pending",   _("Pending")

    event  = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendances")
    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="event_attendances")
    status = models.CharField(max_length=15, choices=AttendanceStatus.choices, default=AttendanceStatus.PENDING)
    notes  = models.CharField(max_length=300, blank=True)

    class Meta:
        unique_together = [("event", "player")]
        verbose_name = _("attendance")

    def __str__(self):
        return f"{self.player} — {self.event} ({self.status})"
