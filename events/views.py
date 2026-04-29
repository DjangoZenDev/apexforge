"""
Events views — calendar, CRUD, fixtures
"""
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from .models import Event, Fixture, Tournament
from .forms import EventForm, FixtureForm, TournamentForm


@login_required
def event_list(request):
    qs = Event.objects.select_related("team").order_by("start_date")
    # Filter by active club via team → club
    club = getattr(request, "active_club", None)
    if club:
        qs = qs.filter(team__club=club)
    event_type = request.GET.get("type")
    status = request.GET.get("status")
    team = request.GET.get("team")
    if event_type:
        qs = qs.filter(event_type=event_type)
    if status:
        qs = qs.filter(status=status)
    if team:
        qs = qs.filter(team_id=team)

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page", 1))
    return render(request, "events/list.html", {
        "page": page,
        "type_choices": Event.Type.choices,
        "status_choices": Event.Status.choices,
    })


@login_required
def calendar_view(request):
    """Full calendar view — events serialized for FullCalendar-like JS rendering."""
    from teams.models import Team
    events_qs = Event.objects.select_related("team")
    club = getattr(request, "active_club", None)
    if club:
        events_qs = events_qs.filter(team__club=club)
    events = events_qs.values(
        "id", "title", "start_date", "start_time", "end_date",
        "event_type", "status", "team__name",
    )

    calendar_events = []
    type_colors = {
        "fixture":    "#059669",
        "training":   "#3b82f6",
        "tournament": "#f59e0b",
        "meeting":    "#8b5cf6",
        "other":      "#6b7280",
    }
    for ev in events:
        calendar_events.append({
            "id":    ev["id"],
            "title": ev["title"],
            "start": str(ev["start_date"]),
            "end":   str(ev["end_date"]) if ev["end_date"] else str(ev["start_date"]),
            "color": type_colors.get(ev["event_type"], "#6b7280"),
            "url":   f"/events/{ev['id']}/",
            "extendedProps": {
                "type": ev["event_type"],
                "status": ev["status"],
                "team": ev["team__name"],
            },
        })

    teams_qs = Team.objects.all()
    if club:
        teams_qs = teams_qs.filter(club=club)
    teams = teams_qs
    legend = [
        ("Fixture",    "#059669"),
        ("Training",   "#3b82f6"),
        ("Tournament", "#f59e0b"),
        ("Meeting",    "#8b5cf6"),
        ("Other",      "#6b7280"),
    ]
    return render(request, "events/calendar.html", {
        "calendar_events_json": json.dumps(calendar_events),
        "teams": teams,
        "legend": legend,
    })


@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event.objects.select_related("team"), pk=pk)
    fixture = getattr(event, "fixture", None)
    attendances = event.attendances.select_related("player")
    return render(request, "events/detail.html", {
        "event": event, "fixture": fixture, "attendances": attendances,
    })


@login_required
def event_create(request):
    form = EventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        event.created_by = request.user
        event.save()
        if event.event_type == Event.Type.FIXTURE:
            Fixture.objects.get_or_create(event=event)
        messages.success(request, _("Event created."))
        return redirect("events:detail", pk=event.pk)
    return render(request, "events/form.html", {"form": form, "title": _("New Event")})


@login_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    form = EventForm(request.POST or None, instance=event)
    fixture_form = None
    if event.event_type == Event.Type.FIXTURE:
        fixture, _ = Fixture.objects.get_or_create(event=event)
        fixture_form = FixtureForm(request.POST or None, instance=fixture, prefix="fixture")

    if request.method == "POST" and form.is_valid():
        form.save()
        if fixture_form and fixture_form.is_valid():
            fixture_form.save()
        messages.success(request, _("Event updated."))
        return redirect("events:detail", pk=pk)
    return render(request, "events/form.html", {
        "form": form, "fixture_form": fixture_form,
        "title": _("Edit Event"), "event": event,
    })


@login_required
@require_POST
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.delete()
    messages.success(request, _("Event deleted."))
    return redirect("events:list")


@login_required
def tournament_list(request):
    tournaments = Tournament.objects.prefetch_related("teams").order_by("-start_date")
    return render(request, "events/tournament_list.html", {"tournaments": tournaments})


@login_required
def tournament_create(request):
    form = TournamentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        tournament = form.save()
        messages.success(request, _("Tournament created."))
        return redirect("events:tournament_list")
    return render(request, "events/tournament_form.html", {"form": form})


@login_required
def events_api(request):
    """JSON endpoint for calendar AJAX requests."""
    start = request.GET.get("start")
    end = request.GET.get("end")
    qs = Event.objects.all()
    if start:
        qs = qs.filter(start_date__gte=start[:10])
    if end:
        qs = qs.filter(start_date__lte=end[:10])

    data = []
    type_colors = {
        "fixture": "#059669", "training": "#3b82f6",
        "tournament": "#f59e0b", "meeting": "#8b5cf6", "other": "#6b7280",
    }
    for ev in qs:
        data.append({
            "id": ev.pk,
            "title": ev.title,
            "start": str(ev.start_date),
            "end": str(ev.end_date or ev.start_date),
            "color": type_colors.get(ev.event_type, "#6b7280"),
            "url": ev.get_absolute_url(),
        })
    return JsonResponse(data, safe=False)


@login_required
def tournament_edit(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    event_form = EventForm(request.POST or None, instance=tournament.event)
    tournament_form = TournamentForm(request.POST or None, instance=tournament)
    if request.method == "POST" and event_form.is_valid() and tournament_form.is_valid():
        event_form.save()
        tournament_form.save()
        messages.success(request, _("Tournament updated."))
        return redirect("events:tournament_list")
    return render(request, "events/tournament_form.html", {
        "event_form": event_form, "tournament_form": tournament_form,
        "title": _("Edit Tournament"), "tournament": tournament,
    })
