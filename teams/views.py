"""
Teams views — CRUD, roster management, CSV import/export
"""
import csv
import io
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from .models import Team, Season, Division, Roster
from .forms import TeamForm, RosterForm, SeasonForm, DivisionForm


@login_required
def team_list(request):
    if request.user.is_fan_investor:
        messages.error(request, _("You do not have permission to view this page."))
        return redirect("fans:portal")
    qs = Team.objects.select_related("division", "season", "manager", "coach", "club")
    # Filter by active club when one is selected
    club = getattr(request, "active_club", None)
    if club:
        qs = qs.filter(club=club)
    sport = request.GET.get("sport")
    status = request.GET.get("status")
    q = request.GET.get("q", "")
    if sport:
        qs = qs.filter(sport=sport)
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(name__icontains=q)

    paginator = Paginator(qs, 12)
    page = paginator.get_page(request.GET.get("page", 1))

    if request.htmx:
        return render(request, "teams/partials/team_cards.html", {"page": page})

    context = {
        "page": page,
        "sports": [("", _("All Sports"))] + list(
            __import__("django.conf", fromlist=["settings"]).settings.APEXFORGE_SPORT_CHOICES
        ),
        "current_sport": sport,
        "current_status": status,
        "query": q,
    }
    return render(request, "teams/list.html", context)


@login_required
def team_detail(request, pk):
    if request.user.is_fan_investor:
        messages.error(request, _("You do not have permission to view this page."))
        return redirect("fans:portal")
    team = get_object_or_404(Team.objects.select_related("division", "season", "manager", "coach"), pk=pk)
    rosters = Roster.objects.filter(team=team, is_active=True).select_related("player", "season")
    return render(request, "teams/detail.html", {"team": team, "rosters": rosters})


@login_required
def team_create(request):
    if not request.user.can_manage:
        messages.error(request, _("Permission denied."))
        return redirect("teams:list")
    form = TeamForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        team = form.save()
        from core.models import ActivityLog
        ActivityLog.log(request.user, ActivityLog.Action.CREATE,
                        f"Created team: {team.name}", "Team", team.pk)
        messages.success(request, _("Team created successfully."))
        return redirect("teams:detail", pk=team.pk)
    return render(request, "teams/form.html", {"form": form, "title": _("New Team")})


@login_required
def team_edit(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if not request.user.can_manage:
        messages.error(request, _("Permission denied."))
        return redirect("teams:detail", pk=pk)
    form = TeamForm(request.POST or None, request.FILES or None, instance=team)
    if request.method == "POST" and form.is_valid():
        team = form.save()
        from core.models import ActivityLog
        ActivityLog.log(request.user, ActivityLog.Action.UPDATE,
                        f"Updated team: {team.name}", "Team", team.pk)
        messages.success(request, _("Team updated."))
        return redirect("teams:detail", pk=team.pk)
    return render(request, "teams/form.html", {"form": form, "title": _("Edit Team"), "team": team})


@login_required
@require_POST
def team_delete(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if not request.user.can_manage:
        messages.error(request, _("Permission denied."))
        return redirect("teams:detail", pk=pk)
    name = team.name
    team.delete()
    from core.models import ActivityLog
    ActivityLog.log(request.user, ActivityLog.Action.DELETE, f"Deleted team: {name}", "Team")
    messages.success(request, _("Team deleted."))
    return redirect("teams:list")


@login_required
def roster_add(request, team_pk):
    team = get_object_or_404(Team, pk=team_pk)
    form = RosterForm(request.POST or None, initial={"team": team})
    if request.method == "POST" and form.is_valid():
        roster = form.save(commit=False)
        roster.team = team
        # Check for duplicate before saving
        already_exists = Roster.objects.filter(
            team=team,
            player=roster.player,
            season=roster.season,
        ).exists()
        if already_exists:
            messages.info(request, _(
                "This player is already on the roster for that season."
            ))
        else:
            roster.save()
            messages.success(request, _("Player added to roster."))
            return redirect("teams:detail", pk=team_pk)
    return render(request, "teams/roster_form.html", {"form": form, "team": team})


@login_required
@require_POST
def generate_demo_squad(request, team_pk):
    """Auto-create 24 demo players and add them to the roster for quick testing."""
    if not request.user.can_manage:
        messages.error(request, _("Permission denied."))
        return redirect("teams:detail", pk=team_pk)

    team = get_object_or_404(Team, pk=team_pk)
    from players.models import Player

    current_season = Season.objects.filter(is_current=True).first()

    # 24 players: 2 GK, 6 DEF, 8 MID, 6 FWD, 2 others
    demo_players = [
        (1,  "GK",  "Goalkeeper"),
        (13, "GK",  "Goalkeeper"),
        (2,  "RB",  "Right Back"),
        (3,  "LB",  "Left Back"),
        (4,  "CB",  "Centre Back"),
        (5,  "CB",  "Centre Back"),
        (6,  "CB",  "Centre Back"),
        (12, "LB",  "Left Back"),
        (8,  "CM",  "Central Midfielder"),
        (15, "CDM", "Defensive Midfielder"),
        (10, "CAM", "Attacking Midfielder"),
        (14, "CM",  "Central Midfielder"),
        (16, "CM",  "Central Midfielder"),
        (18, "CM",  "Central Midfielder"),
        (20, "CDM", "Defensive Midfielder"),
        (22, "CAM", "Attacking Midfielder"),
        (7,  "RW",  "Right Winger"),
        (11, "LW",  "Left Winger"),
        (9,  "ST",  "Striker"),
        (17, "ST",  "Striker"),
        (19, "RW",  "Right Winger"),
        (21, "LW",  "Left Winger"),
        (23, "CF",  "Centre Forward"),
        (24, "SUB", "Centre Back"),
    ]

    created = 0
    for jersey, short_pos, full_pos in demo_players:
        player_name = f"{team.short_name or team.name[:6]} Player {jersey:02d}"
        player, _pc = Player.objects.get_or_create(
            full_name=player_name,
            defaults={
                "sport": team.sport,
                "position": full_pos,
                "status": "active",
                "jersey_number": jersey,
            },
        )
        _rc, made = Roster.objects.get_or_create(
            team=team, player=player, season=current_season,
            defaults={"jersey_number": jersey, "position": full_pos, "is_active": True},
        )
        if made:
            created += 1

    messages.success(request, _(f"Generated {created} demo players for {team.name}."))
    return redirect("teams:detail", pk=team_pk)


@login_required
def season_list(request):
    """List all seasons and allow creating new ones."""
    if not request.user.can_manage:
        messages.error(request, _("Permission denied."))
        return redirect("teams:list")
    from .forms import SeasonForm
    seasons = Season.objects.order_by("-start_date")
    form = SeasonForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Season created."))
        return redirect("teams:seasons")
    return render(request, "teams/seasons.html", {"seasons": seasons, "form": form})


@login_required
def season_set_current(request, pk):
    if not request.user.can_manage:
        messages.error(request, _("Permission denied."))
        return redirect("teams:seasons")
    season = get_object_or_404(Season, pk=pk)
    Season.objects.all().update(is_current=False)
    season.is_current = True
    season.save(update_fields=["is_current"])
    messages.success(request, _(f"'{season.name}' is now the current season."))
    return redirect("teams:seasons")


@login_required
def season_delete(request, pk):
    if not request.user.can_manage:
        messages.error(request, _("Permission denied."))
        return redirect("teams:seasons")
    season = get_object_or_404(Season, pk=pk)
    if request.method == "POST":
        season.delete()
        messages.success(request, _("Season deleted."))
    return redirect("teams:seasons")


@login_required
def export_roster_csv(request, pk):
    if not request.user.can_manage:
        messages.error(request, _("Permission denied."))
        return redirect("teams:list")
    team = get_object_or_404(Team, pk=pk)
    rosters = Roster.objects.filter(team=team).select_related("player")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{team.name}_roster.csv"'

    writer = csv.writer(response)
    writer.writerow(["#", "Name", "Position", "Nationality", "Date of Birth", "Captain"])
    for r in rosters:
        writer.writerow([
            r.jersey_number or "",
            r.player.full_name,
            r.position,
            r.player.nationality,
            r.player.date_of_birth or "",
            "Yes" if r.is_captain else "No",
        ])
    return response


@login_required
@require_POST
def import_roster_csv(request, pk):
    if not request.user.can_manage:
        messages.error(request, _("Permission denied."))
        return redirect("teams:detail", pk=pk)
    team = get_object_or_404(Team, pk=pk)
    csv_file = request.FILES.get("csv_file")
    if not csv_file:
        messages.error(request, _("Please upload a CSV file."))
        return redirect("teams:detail", pk=pk)

    decoded = csv_file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))
    from players.models import Player

    created = 0
    for row in reader:
        name = row.get("Name", "").strip()
        if not name:
            continue
        player, _ = Player.objects.get_or_create(
            full_name=name,
            defaults={"position": row.get("Position", ""), "nationality": row.get("Nationality", "")},
        )
        season = Season.objects.filter(is_current=True).first()
        Roster.objects.get_or_create(team=team, player=player, season=season,
                                     defaults={"jersey_number": row.get("#") or None,
                                               "position": row.get("Position", "")})
        created += 1

    messages.success(request, _(f"Imported {created} players."))
    return redirect("teams:detail", pk=pk)
