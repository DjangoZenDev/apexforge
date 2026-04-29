from django.contrib import admin
from .models import Team, Season, Division, Roster


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_current")
    list_editable = ("is_current",)


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "sport")
    list_filter = ("sport",)


class RosterInline(admin.TabularInline):
    model = Roster
    extra = 0
    fields = ("player", "jersey_number", "position", "is_captain", "is_active")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display  = ("name", "sport", "division", "status", "player_count")
    list_filter   = ("sport", "status", "division")
    search_fields = ("name", "city", "country")
    inlines       = [RosterInline]


@admin.register(Roster)
class RosterAdmin(admin.ModelAdmin):
    list_display  = ("player", "team", "jersey_number", "position", "is_active")
    list_filter   = ("team", "is_active")
    search_fields = ("player__full_name", "team__name")
