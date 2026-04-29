"""
Scouting views — reports, talent database, watchlists
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from .models import ScoutReport, TalentProfile, Watchlist
from .forms import ScoutReportForm, TalentProfileForm, WatchlistForm


def _require_scout_or_manager(request):
    """Return a redirect response if the user is a fan/investor, else None."""
    if request.user.is_fan_investor:
        messages.error(request, _("You do not have permission to access scouting."))
        return redirect("fans:portal")
    return None


@login_required
def scouting_dashboard(request):
    denied = _require_scout_or_manager(request)
    if denied:
        return denied
    reports = ScoutReport.objects.select_related("player", "scout").order_by("-created_at")[:10]
    top_talents = TalentProfile.objects.order_by("-rating")[:10]
    my_watchlists = Watchlist.objects.filter(owner=request.user).prefetch_related("players")
    total_reports = ScoutReport.objects.count()
    total_talents = TalentProfile.objects.count()
    pending_trials = TalentProfile.objects.filter(status=TalentProfile.Status.TRIALING).count()

    return render(request, "scouting/dashboard.html", {
        "reports": reports,
        "top_talents": top_talents,
        "my_watchlists": my_watchlists,
        "total_reports": total_reports,
        "total_talents": total_talents,
        "pending_trials": pending_trials,
    })


@login_required
def talent_list(request):
    denied = _require_scout_or_manager(request)
    if denied:
        return denied
    qs = TalentProfile.objects.all()
    q = request.GET.get("q", "")
    status = request.GET.get("status")
    position = request.GET.get("position")
    min_rating = request.GET.get("min_rating")

    if q:
        qs = qs.filter(full_name__icontains=q)
    if status:
        qs = qs.filter(status=status)
    if position:
        qs = qs.filter(position__icontains=position)
    if min_rating:
        qs = qs.filter(rating__gte=min_rating)

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page", 1))

    if request.htmx:
        return render(request, "scouting/partials/talent_rows.html", {"page": page})

    return render(request, "scouting/talent_list.html", {
        "page": page, "query": q,
        "status_choices": TalentProfile.Status.choices,
        "current_status": status,
    })


@login_required
def talent_detail(request, pk):
    denied = _require_scout_or_manager(request)
    if denied:
        return denied
    talent = get_object_or_404(TalentProfile, pk=pk)
    reports = []  # ScoutReport links to Player, not TalentProfile
    return render(request, "scouting/talent_detail.html", {"talent": talent, "reports": reports})


@login_required
def talent_create(request):
    denied = _require_scout_or_manager(request)
    if denied:
        return denied
    form = TalentProfileForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        talent = form.save(commit=False)
        talent.added_by = request.user
        talent.save()
        messages.success(request, _("Talent added."))
        return redirect("scouting:talent_detail", pk=talent.pk)
    return render(request, "scouting/talent_form.html", {"form": form, "title": _("Add Talent")})


@login_required
def talent_edit(request, pk):
    denied = _require_scout_or_manager(request)
    if denied:
        return denied
    talent = get_object_or_404(TalentProfile, pk=pk)
    form = TalentProfileForm(request.POST or None, request.FILES or None, instance=talent)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Talent updated."))
        return redirect("scouting:talent_detail", pk=pk)
    return render(request, "scouting/talent_form.html", {"form": form, "talent": talent, "title": _("Edit Talent")})


@login_required
def report_create(request):
    denied = _require_scout_or_manager(request)
    if denied:
        return denied
    form = ScoutReportForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        report = form.save(commit=False)
        report.scout = request.user
        # Auto-calculate overall as average of 4 categories
        report.overall = round(
            (report.technical + report.tactical + report.physical + report.mental) / 4, 2
        )
        report.save()
        messages.success(request, _("Scout report submitted."))
        return redirect("scouting:report_detail", pk=report.pk)
    return render(request, "scouting/report_form.html", {"form": form})


@login_required
def report_detail(request, pk):
    denied = _require_scout_or_manager(request)
    if denied:
        return denied
    report = get_object_or_404(ScoutReport.objects.select_related("player", "scout"), pk=pk)
    ratings = [
        ("Technical", report.technical),
        ("Physical",  report.physical),
        ("Tactical",  report.tactical),
        ("Mental",    report.mental),
    ]
    return render(request, "scouting/report_detail.html", {"report": report, "ratings": ratings})


@login_required
def report_list(request):
    denied = _require_scout_or_manager(request)
    if denied:
        return denied
    qs = ScoutReport.objects.select_related("player", "scout").order_by("-created_at")
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page", 1))
    return render(request, "scouting/report_list.html", {"page": page})


@login_required
def watchlist_view(request):
    denied = _require_scout_or_manager(request)
    if denied:
        return denied
    watchlists = Watchlist.objects.filter(owner=request.user).prefetch_related("players", "talents")
    form = WatchlistForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        wl = form.save(commit=False)
        wl.owner = request.user
        wl.save()
        messages.success(request, _("Watchlist created."))
        return redirect("scouting:watchlist")
    return render(request, "scouting/watchlist.html", {"watchlists": watchlists, "form": form})


@login_required
@require_POST
def watchlist_add_player(request, wl_pk, player_pk):
    wl = get_object_or_404(Watchlist, pk=wl_pk, owner=request.user)
    from players.models import Player
    player = get_object_or_404(Player, pk=player_pk)
    wl.players.add(player)
    if request.htmx:
        from django.http import HttpResponse
        return HttpResponse(
            f'<span class="text-emerald-600 text-sm font-medium">Added to {wl.name}</span>'
        )
    messages.success(request, _(f"Added {player.full_name} to {wl.name}."))
    return redirect("players:detail", pk=player_pk)


@login_required
def report_edit(request, pk):
    report = get_object_or_404(ScoutReport, pk=pk)
    form = ScoutReportForm(request.POST or None, instance=report)
    if request.method == "POST" and form.is_valid():
        r = form.save(commit=False)
        r.overall = round((r.technical + r.tactical + r.physical + r.mental) / 4, 2)
        r.save()
        messages.success(request, _("Report updated."))
        return redirect("scouting:report_detail", pk=pk)
    return render(request, "scouting/report_form.html", {"form": form, "report": report})


@login_required
@require_POST
def watchlist_remove_player(request, pk):
    from players.models import Player
    player = get_object_or_404(Player, pk=pk)
    wl = Watchlist.objects.filter(owner=request.user).first()
    if wl:
        wl.players.remove(player)
    return redirect("scouting:watchlist")


@login_required
@require_POST
def watchlist_remove_talent(request, pk):
    talent = get_object_or_404(TalentProfile, pk=pk)
    wl = Watchlist.objects.filter(owner=request.user).first()
    if wl:
        wl.talents.remove(talent)
    return redirect("scouting:watchlist")
