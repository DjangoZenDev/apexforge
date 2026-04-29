from django.contrib import admin
from .models import Competition, Stage, Group, Match, Standing


class StageInline(admin.TabularInline):
    model = Stage
    extra = 0


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ["name", "competition_type", "status", "season", "start_date", "end_date"]
    list_filter = ["status", "competition_type", "sport"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [StageInline]


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ["home_team", "away_team", "competition", "date", "status", "result_display"]
    list_filter = ["status", "competition"]
    search_fields = ["home_team__name", "away_team__name"]


@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ["team", "competition", "played", "won", "drawn", "lost", "goals_for", "goals_against", "points"]
    list_filter = ["competition"]
