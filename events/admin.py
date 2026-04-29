from django.contrib import admin
from .models import Event, Fixture, Tournament, EventAttendance


class FixtureInline(admin.StackedInline):
    model = Fixture
    can_delete = False
    extra = 0


class AttendanceInline(admin.TabularInline):
    model = EventAttendance
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display  = ("title", "event_type", "team", "start_date", "status")
    list_filter   = ("event_type", "status", "team")
    search_fields = ("title", "venue", "opponent")
    date_hierarchy = "start_date"
    inlines       = [FixtureInline, AttendanceInline]


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("name", "sport", "start_date", "end_date", "location")
    filter_horizontal = ("teams",)
