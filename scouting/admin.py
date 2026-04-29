from django.contrib import admin
from .models import ScoutReport, TalentProfile, Watchlist


@admin.register(ScoutReport)
class ScoutReportAdmin(admin.ModelAdmin):
    list_display  = ("player", "scout", "match_date", "overall", "recommendation")
    list_filter   = ("recommendation",)
    search_fields = ("player__full_name", "scout__email")


@admin.register(TalentProfile)
class TalentProfileAdmin(admin.ModelAdmin):
    list_display  = ("full_name", "position", "current_club", "status", "rating")
    list_filter   = ("status",)
    search_fields = ("full_name", "current_club", "nationality")


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("name", "owner")
    filter_horizontal = ("players", "talents")
