"""
Tournaments — Competitions, Stages, Groups, Matches, Standings
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Competition(models.Model):
    class Type(models.TextChoices):
        LEAGUE         = "league",          _("League")
        CUP            = "cup",             _("Cup / Knockout")
        GROUP_KNOCKOUT = "group_knockout",  _("Group Stage + Knockout")
        ROUND_ROBIN    = "round_robin",     _("Round Robin")
        FRIENDLY       = "friendly",        _("Friendly Tournament")

    class Status(models.TextChoices):
        DRAFT     = "draft",     _("Draft")
        UPCOMING  = "upcoming",  _("Upcoming")
        ACTIVE    = "active",    _("Active")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    name             = models.CharField(max_length=200)
    slug             = models.SlugField(unique=True)
    sport            = models.CharField(max_length=50, choices=settings.APEXFORGE_SPORT_CHOICES, default="football")
    competition_type = models.CharField(max_length=20, choices=Type.choices, default=Type.LEAGUE)
    status           = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    season           = models.CharField(max_length=20, blank=True, help_text="e.g. 2026-27")
    teams            = models.ManyToManyField("teams.Team", blank=True, related_name="competitions")
    start_date       = models.DateField()
    end_date         = models.DateField()
    description      = models.TextField(blank=True)
    logo             = models.ImageField(upload_to="tournaments/logos/", null=True, blank=True)
    prize_pool       = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_by       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                         null=True, related_name="created_competitions")
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name

    @property
    def played_matches(self):
        return self.matches.filter(status=Match.Status.COMPLETED).count()


class Stage(models.Model):
    class Type(models.TextChoices):
        GROUP    = "group",    _("Group Stage")
        KNOCKOUT = "knockout", _("Knockout Round")
        FINAL    = "final",    _("Final")
        SEMIFINAL= "semifinal",_("Semi-Final")
        QF       = "qf",       _("Quarter-Final")
        R16      = "r16",      _("Round of 16")

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="stages")
    name        = models.CharField(max_length=100)
    stage_type  = models.CharField(max_length=20, choices=Type.choices)
    order       = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.competition} — {self.name}"


class Group(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="groups")
    name  = models.CharField(max_length=50)
    teams = models.ManyToManyField("teams.Team", blank=True, related_name="tournament_groups")

    def __str__(self):
        return f"{self.stage} / {self.name}"


class Match(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", _("Scheduled")
        LIVE      = "live",      _("Live")
        COMPLETED = "completed", _("Completed")
        POSTPONED = "postponed", _("Postponed")
        CANCELLED = "cancelled", _("Cancelled")

    competition  = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="matches")
    stage        = models.ForeignKey(Stage, on_delete=models.SET_NULL, null=True, blank=True, related_name="matches")
    group        = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name="matches")
    home_team    = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="home_tournament_matches")
    away_team    = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="away_tournament_matches")
    date         = models.DateTimeField()
    venue        = models.CharField(max_length=200, blank=True)
    home_score   = models.PositiveSmallIntegerField(null=True, blank=True)
    away_score   = models.PositiveSmallIntegerField(null=True, blank=True)
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    round_number = models.PositiveSmallIntegerField(null=True, blank=True)
    notes        = models.TextField(blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"

    @property
    def result_display(self):
        if self.home_score is not None and self.away_score is not None:
            return f"{self.home_score} – {self.away_score}"
        return "— vs —"

    @property
    def winner(self):
        if self.home_score is None or self.away_score is None:
            return None
        if self.home_score > self.away_score:
            return self.home_team
        if self.away_score > self.home_score:
            return self.away_team
        return None


class Lineup(models.Model):
    FORMATION_CHOICES = [
        ("4-4-2",   "4-4-2"),
        ("4-3-3",   "4-3-3"),
        ("4-2-3-1", "4-2-3-1"),
        ("3-5-2",   "3-5-2"),
        ("5-3-2",   "5-3-2"),
        ("4-1-4-1", "4-1-4-1"),
        ("3-4-3",   "3-4-3"),
    ]

    match      = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="lineups")
    team       = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="lineups")
    formation  = models.CharField(max_length=10, choices=FORMATION_CHOICES, default="4-4-2")
    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("match", "team")]
        verbose_name = _("lineup")
        verbose_name_plural = _("lineups")

    def __str__(self):
        return f"{self.team} — {self.match} ({self.formation})"


class LineupPlayer(models.Model):
    lineup         = models.ForeignKey(Lineup, on_delete=models.CASCADE, related_name="entries")
    player         = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="lineup_entries")
    position_slot  = models.CharField(max_length=10, blank=True)   # e.g. "CB1", "LW"
    position_label = models.CharField(max_length=20, blank=True)   # e.g. "CB", "LW"
    shirt_number   = models.PositiveSmallIntegerField(null=True, blank=True)
    is_substitute  = models.BooleanField(default=False)
    is_captain     = models.BooleanField(default=False)
    sub_order      = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = [("lineup", "player")]
        ordering = ["is_substitute", "sub_order"]
        verbose_name = _("lineup player")
        verbose_name_plural = _("lineup players")

    def __str__(self):
        return f"{self.player} ({self.lineup})"


class Standing(models.Model):
    competition   = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="standings")
    group         = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name="standings")
    team          = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="standings")
    played        = models.PositiveSmallIntegerField(default=0)
    won           = models.PositiveSmallIntegerField(default=0)
    drawn         = models.PositiveSmallIntegerField(default=0)
    lost          = models.PositiveSmallIntegerField(default=0)
    goals_for     = models.PositiveSmallIntegerField(default=0)
    goals_against = models.PositiveSmallIntegerField(default=0)
    points        = models.SmallIntegerField(default=0)

    class Meta:
        ordering      = ["-points", "-goals_for"]
        unique_together = [("competition", "group", "team")]

    def __str__(self):
        return f"{self.team} — {self.points} pts"

    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against

    def recalculate(self):
        matches = Match.objects.filter(
            competition=self.competition, status=Match.Status.COMPLETED,
        ).filter(
            models.Q(home_team=self.team) | models.Q(away_team=self.team)
        )
        if self.group:
            matches = matches.filter(group=self.group)
        p = w = d = l = gf = ga = 0
        for m in matches:
            if m.home_score is None:
                continue
            p += 1
            if m.home_team == self.team:
                gf += m.home_score; ga += m.away_score
                if m.home_score > m.away_score: w += 1
                elif m.home_score == m.away_score: d += 1
                else: l += 1
            else:
                gf += m.away_score; ga += m.home_score
                if m.away_score > m.home_score: w += 1
                elif m.away_score == m.home_score: d += 1
                else: l += 1
        self.played = p; self.won = w; self.drawn = d; self.lost = l
        self.goals_for = gf; self.goals_against = ga
        self.points = w * 3 + d
        self.save()
