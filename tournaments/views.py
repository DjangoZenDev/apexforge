"""Tournaments views — competitions, matches, standings, lineups"""
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from .models import Competition, Stage, Group, Match, Standing, Lineup, LineupPlayer
from .forms import CompetitionForm, MatchForm, StandingForm


@login_required
def competition_list(request):
    qs = Competition.objects.prefetch_related("teams").order_by("-start_date")
    status = request.GET.get("status")
    sport = request.GET.get("sport")
    if status:
        qs = qs.filter(status=status)
    if sport:
        qs = qs.filter(sport=sport)
    return render(request, "tournaments/competition_list.html", {
        "competitions": qs,
        "status_choices": Competition.Status.choices,
    })


@login_required
def competition_detail(request, slug):
    comp = get_object_or_404(Competition.objects.prefetch_related("teams", "stages__groups__teams"), slug=slug)
    standings = comp.standings.select_related("team", "group").order_by("group__name", "-points")
    matches = comp.matches.select_related("home_team", "away_team", "stage", "group").order_by("date")
    return render(request, "tournaments/competition_detail.html", {
        "competition": comp,
        "standings": standings,
        "matches": matches,
        "Match": Match,
    })


@login_required
def competition_create(request):
    form = CompetitionForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        comp = form.save(commit=False)
        comp.created_by = request.user
        if not comp.slug:
            comp.slug = slugify(comp.name)
        comp.save()
        form.save_m2m()
        messages.success(request, _("Competition created."))
        return redirect("tournaments:detail", slug=comp.slug)
    return render(request, "tournaments/competition_form.html", {"form": form, "title": _("New Competition")})


@login_required
def competition_edit(request, slug):
    comp = get_object_or_404(Competition, slug=slug)
    form = CompetitionForm(request.POST or None, request.FILES or None, instance=comp)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Competition updated."))
        return redirect("tournaments:detail", slug=comp.slug)
    return render(request, "tournaments/competition_form.html", {
        "form": form, "title": _("Edit Competition"), "competition": comp,
    })


@login_required
def match_create(request, competition_slug):
    comp = get_object_or_404(Competition, slug=competition_slug)
    form = MatchForm(request.POST or None, competition=comp)
    if request.method == "POST" and form.is_valid():
        match = form.save(commit=False)
        match.competition = comp
        match.save()
        # Update standings if match is completed
        if match.status == Match.Status.COMPLETED:
            _update_standings(match)
        messages.success(request, _("Match added."))
        return redirect("tournaments:detail", slug=competition_slug)
    return render(request, "tournaments/match_form.html", {"form": form, "competition": comp})


@login_required
def match_edit(request, pk):
    match = get_object_or_404(Match, pk=pk)
    form = MatchForm(request.POST or None, instance=match, competition=match.competition)
    if request.method == "POST" and form.is_valid():
        form.save()
        if match.status == Match.Status.COMPLETED:
            _update_standings(match)
        messages.success(request, _("Match updated."))
        return redirect("tournaments:detail", slug=match.competition.slug)
    return render(request, "tournaments/match_form.html", {"form": form, "match": match,
                                                            "competition": match.competition})


@login_required
def standings_view(request, slug):
    comp = get_object_or_404(Competition, slug=slug)
    standings = comp.standings.select_related("team", "group").order_by("group__name", "-points")
    return render(request, "tournaments/standings.html", {"competition": comp, "standings": standings})


@login_required
def lineup_builder(request, pk):
    match = get_object_or_404(
        Match.objects.select_related("home_team", "away_team", "competition"), pk=pk
    )

    def _squad(team):
        from teams.models import Roster
        from players.models import Player
        # Try with is_active filter first, fall back to all roster entries
        pks = list(Roster.objects.filter(team=team, is_active=True).values_list("player_id", flat=True))
        if not pks:
            # Fallback: pick up any roster entry for this team regardless of is_active
            pks = list(Roster.objects.filter(team=team).values_list("player_id", flat=True))
        return list(
            Player.objects.filter(pk__in=pks)
            .values("pk", "full_name", "position", "jersey_number", "status")
            .order_by("position", "full_name")
        )

    home_lineup, _ = Lineup.objects.get_or_create(
        match=match, team=match.home_team, defaults={"formation": "4-4-2"}
    )
    away_lineup, _ = Lineup.objects.get_or_create(
        match=match, team=match.away_team, defaults={"formation": "4-4-2"}
    )

    def _entries(lineup):
        starters = {}
        subs = []
        for e in lineup.entries.select_related("player"):
            p = {
                "id": e.player.pk, "name": e.player.full_name,
                "shirt": e.shirt_number or "", "is_captain": e.is_captain,
                "position": e.player.position or "",
            }
            if e.is_substitute:
                subs.append(p)
            else:
                starters[e.position_slot] = p
        return starters, subs

    home_starters, home_subs = _entries(home_lineup)
    away_starters, away_subs = _entries(away_lineup)

    home_squad_list = _squad(match.home_team)
    away_squad_list = _squad(match.away_team)

    ctx = {
        "match":            match,
        "home_lineup":      home_lineup,
        "away_lineup":      away_lineup,
        "home_squad":       json.dumps(home_squad_list),
        "away_squad":       json.dumps(away_squad_list),
        "home_squad_count": len(home_squad_list),
        "away_squad_count": len(away_squad_list),
        "home_starters":  json.dumps(home_starters),
        "away_starters":  json.dumps(away_starters),
        "home_subs":      json.dumps(home_subs),
        "away_subs":      json.dumps(away_subs),
        "formation_choices": Lineup.FORMATION_CHOICES,
    }
    return render(request, "tournaments/lineup_builder.html", ctx)


@login_required
@require_POST
def lineup_save(request, pk):
    match = get_object_or_404(Match, pk=pk)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    team_id = int(data.get("team_id", 0))
    if team_id == match.home_team_id:
        team = match.home_team
    elif team_id == match.away_team_id:
        team = match.away_team
    else:
        return JsonResponse({"status": "error", "message": "Unknown team"}, status=400)

    from players.models import Player

    lineup, _ = Lineup.objects.get_or_create(match=match, team=team)
    lineup.formation = data.get("formation", "4-4-2")
    lineup.save()
    lineup.entries.all().delete()

    for entry in data.get("starters", []):
        try:
            player = Player.objects.get(pk=entry["player_id"])
            LineupPlayer.objects.create(
                lineup=lineup, player=player,
                position_slot=entry.get("position_slot", ""),
                position_label=entry.get("position_label", ""),
                shirt_number=entry.get("shirt") or None,
                is_substitute=False,
                is_captain=entry.get("is_captain", False),
            )
        except Player.DoesNotExist:
            pass

    for i, entry in enumerate(data.get("substitutes", [])):
        try:
            player = Player.objects.get(pk=entry["player_id"])
            LineupPlayer.objects.create(
                lineup=lineup, player=player,
                shirt_number=entry.get("shirt") or None,
                is_substitute=True, sub_order=i,
            )
        except Player.DoesNotExist:
            pass

    return JsonResponse({"status": "ok", "message": str(_("Lineup saved successfully."))})


def _update_standings(match):
    """Recalculate standings for both teams after a match result."""
    for team in [match.home_team, match.away_team]:
        standing, _ = Standing.objects.get_or_create(
            competition=match.competition,
            group=match.group,
            team=team,
        )
        standing.recalculate()
