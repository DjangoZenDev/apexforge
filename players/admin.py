from django.contrib import admin
from .models import Player, PlayerStats, InjuryLog, PerformanceMetric


class PlayerStatsInline(admin.TabularInline):
    model = PlayerStats
    extra = 0


class InjuryLogInline(admin.TabularInline):
    model = InjuryLog
    extra = 0


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display  = ("full_name", "position", "nationality", "age", "status", "sport")
    list_filter   = ("status", "sport", "preferred_foot")
    search_fields = ("full_name", "nationality", "position")
    inlines       = [PlayerStatsInline, InjuryLogInline]
    readonly_fields = ("age", "current_team")


@admin.register(PlayerStats)
class PlayerStatsAdmin(admin.ModelAdmin):
    list_display = ("player", "team", "season", "appearances", "goals", "assists", "rating")
    list_filter  = ("team", "season")


@admin.register(InjuryLog)
class InjuryLogAdmin(admin.ModelAdmin):
    list_display = ("player", "injury_type", "severity", "injury_date", "is_active")
    list_filter  = ("severity",)


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ("player", "metric", "value", "unit", "date")
    list_filter  = ("metric",)
