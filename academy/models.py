"""
Academy — Youth development programs, development plans, milestones
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AgeGroup(models.TextChoices):
    U8     = "u8",     _("Under 8")
    U10    = "u10",    _("Under 10")
    U12    = "u12",    _("Under 12")
    U14    = "u14",    _("Under 14")
    U16    = "u16",    _("Under 16")
    U18    = "u18",    _("Under 18")
    U21    = "u21",    _("Under 21")
    SENIOR = "senior", _("Senior")


class AcademyProgram(models.Model):
    name        = models.CharField(max_length=200)
    age_group   = models.CharField(max_length=10, choices=AgeGroup.choices)
    description = models.TextField(blank=True)
    head_coach  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name="academy_programs")
    team        = models.ForeignKey("teams.Team", on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="academy_programs")
    start_date  = models.DateField()
    end_date    = models.DateField(null=True, blank=True)
    max_players = models.PositiveSmallIntegerField(default=25)
    is_active   = models.BooleanField(default=True)
    goals       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_age_group_display()})"

    @property
    def player_count(self):
        return self.development_plans.values("player").distinct().count()


class DevelopmentPlan(models.Model):
    player           = models.ForeignKey("players.Player", on_delete=models.CASCADE,
                                         related_name="development_plans")
    program          = models.ForeignKey(AcademyProgram, on_delete=models.CASCADE,
                                         related_name="development_plans")
    season           = models.CharField(max_length=20, help_text="e.g. 2024-25")
    goals            = models.TextField()
    strengths        = models.TextField(blank=True)
    areas_to_improve = models.TextField(blank=True)
    technical_rating = models.PositiveSmallIntegerField(default=5)
    tactical_rating  = models.PositiveSmallIntegerField(default=5)
    physical_rating  = models.PositiveSmallIntegerField(default=5)
    mental_rating    = models.PositiveSmallIntegerField(default=5)
    overall_rating   = models.PositiveSmallIntegerField(default=5)
    coach_notes      = models.TextField(blank=True)
    created_by       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                         null=True, related_name="created_dev_plans")
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering        = ["-updated_at"]
        unique_together = [("player", "program", "season")]

    def __str__(self):
        return f"{self.player} — {self.program} ({self.season})"


class DevelopmentMilestone(models.Model):
    plan          = models.ForeignKey(DevelopmentPlan, on_delete=models.CASCADE, related_name="milestones")
    title         = models.CharField(max_length=200)
    description   = models.TextField(blank=True)
    target_date   = models.DateField()
    achieved      = models.BooleanField(default=False)
    achieved_date = models.DateField(null=True, blank=True)
    notes         = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["target_date"]

    def __str__(self):
        return f"{'✓' if self.achieved else '○'} {self.title}"
