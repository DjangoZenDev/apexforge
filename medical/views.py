"""Medical views — injury list, detail, recovery plans, treatments, medical records"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _

from core.decorators import staff_required, manager_required
from players.models import Player
from .models import Injury, RecoveryPlan, Treatment, MedicalRecord
from .forms import InjuryForm, RecoveryPlanForm, TreatmentForm, MedicalRecordForm


@staff_required
def injury_list(request):
    qs = Injury.objects.select_related("player", "reported_by").order_by("-injury_date")
    club = getattr(request, "active_club", None)
    if club:
        qs = qs.filter(player__rosters__team__club=club).distinct()
    status = request.GET.get("status")
    severity = request.GET.get("severity")
    q = request.GET.get("q", "")
    if status:
        qs = qs.filter(status=status)
    if severity:
        qs = qs.filter(severity=severity)
    if q:
        qs = qs.filter(Q(player__first_name__icontains=q) | Q(player__last_name__icontains=q)
                       | Q(injury_type__icontains=q))
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page", 1))
    return render(request, "medical/injury_list.html", {
        "page": page,
        "status_choices": Injury.Status.choices,
        "severity_choices": Injury.Severity.choices,
    })


@staff_required
def injury_detail(request, pk):
    injury = get_object_or_404(Injury.objects.select_related("player", "reported_by"), pk=pk)
    treatments = injury.treatments.order_by("-date")
    recovery_plan = getattr(injury, "recovery_plan", None)
    return render(request, "medical/injury_detail.html", {
        "injury": injury,
        "treatments": treatments,
        "recovery_plan": recovery_plan,
    })


@staff_required
def injury_create(request, player_pk=None):
    player = get_object_or_404(Player, pk=player_pk) if player_pk else None
    initial = {"player": player} if player else {}
    form = InjuryForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        injury = form.save(commit=False)
        injury.reported_by = request.user
        injury.save()
        messages.success(request, _("Injury recorded."))
        return redirect("medical:injury_detail", pk=injury.pk)
    return render(request, "medical/injury_form.html", {"form": form, "title": _("Report Injury")})


@staff_required
def injury_edit(request, pk):
    injury = get_object_or_404(Injury, pk=pk)
    form = InjuryForm(request.POST or None, instance=injury)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Injury updated."))
        return redirect("medical:injury_detail", pk=pk)
    return render(request, "medical/injury_form.html", {"form": form, "title": _("Edit Injury"), "injury": injury})


@staff_required
def treatment_add(request, injury_pk):
    injury = get_object_or_404(Injury, pk=injury_pk)
    form = TreatmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        t = form.save(commit=False)
        t.injury = injury
        t.save()
        messages.success(request, _("Treatment added."))
        return redirect("medical:injury_detail", pk=injury_pk)
    return render(request, "medical/treatment_form.html", {"form": form, "injury": injury})


@staff_required
def recovery_plan_create(request, injury_pk):
    injury = get_object_or_404(Injury, pk=injury_pk)
    form = RecoveryPlanForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        plan = form.save(commit=False)
        plan.injury = injury
        plan.save()
        messages.success(request, _("Recovery plan created."))
        return redirect("medical:injury_detail", pk=injury_pk)
    return render(request, "medical/recovery_form.html", {"form": form, "injury": injury})


@staff_required
def recovery_plan_edit(request, pk):
    plan = get_object_or_404(RecoveryPlan, pk=pk)
    form = RecoveryPlanForm(request.POST or None, instance=plan)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Recovery plan updated."))
        return redirect("medical:injury_detail", pk=plan.injury.pk)
    return render(request, "medical/recovery_form.html", {"form": form, "injury": plan.injury})


@staff_required
def medical_records(request, player_pk):
    player = get_object_or_404(Player, pk=player_pk)
    records = player.medical_records.order_by("-date")
    if not request.user.can_manage:
        records = records.filter(is_confidential=False)
    return render(request, "medical/records.html", {"player": player, "records": records})


@staff_required
def medical_record_create(request, player_pk):
    player = get_object_or_404(Player, pk=player_pk)
    form = MedicalRecordForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        rec = form.save(commit=False)
        rec.player = player
        rec.created_by = request.user
        rec.save()
        messages.success(request, _("Medical record added."))
        return redirect("medical:records", player_pk=player_pk)
    return render(request, "medical/record_form.html", {"form": form, "player": player})
