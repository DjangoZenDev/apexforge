"""Academy & Youth Development views"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _

from players.models import Player
from .models import AcademyProgram, DevelopmentPlan, DevelopmentMilestone, AgeGroup
from .forms import AcademyProgramForm, DevelopmentPlanForm, MilestoneForm


@login_required
def program_list(request):
    programs = AcademyProgram.objects.select_related("head_coach", "team").filter(is_active=True)
    age_group = request.GET.get("age_group")
    if age_group:
        programs = programs.filter(age_group=age_group)
    return render(request, "academy/programs.html", {
        "programs": programs,
        "age_group_choices": AgeGroup.choices,
    })


@login_required
def program_detail(request, pk):
    program = get_object_or_404(AcademyProgram, pk=pk)
    plans = program.development_plans.select_related("player", "created_by").order_by("player__last_name")
    return render(request, "academy/program_detail.html", {"program": program, "plans": plans})


@login_required
def program_create(request):
    form = AcademyProgramForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Academy program created."))
        return redirect("academy:programs")
    return render(request, "academy/program_form.html", {"form": form, "title": _("New Program")})


@login_required
def program_edit(request, pk):
    program = get_object_or_404(AcademyProgram, pk=pk)
    form = AcademyProgramForm(request.POST or None, instance=program)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Program updated."))
        return redirect("academy:program_detail", pk=pk)
    return render(request, "academy/program_form.html", {
        "form": form, "title": _("Edit Program"), "program": program,
    })


@login_required
def plan_create(request, program_pk, player_pk=None):
    program = get_object_or_404(AcademyProgram, pk=program_pk)
    initial = {}
    if player_pk:
        player = get_object_or_404(Player, pk=player_pk)
        initial["player"] = player
    form = DevelopmentPlanForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        plan = form.save(commit=False)
        plan.program = program
        plan.created_by = request.user
        plan.save()
        messages.success(request, _("Development plan created."))
        return redirect("academy:plan_detail", pk=plan.pk)
    return render(request, "academy/plan_form.html", {"form": form, "program": program})


@login_required
def plan_detail(request, pk):
    plan = get_object_or_404(
        DevelopmentPlan.objects.select_related("player", "program", "created_by")
                               .prefetch_related("milestones"),
        pk=pk
    )
    milestone_form = MilestoneForm()
    return render(request, "academy/plan_detail.html", {
        "plan": plan, "milestone_form": milestone_form,
    })


@login_required
def plan_edit(request, pk):
    plan = get_object_or_404(DevelopmentPlan, pk=pk)
    form = DevelopmentPlanForm(request.POST or None, instance=plan)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Development plan updated."))
        return redirect("academy:plan_detail", pk=pk)
    return render(request, "academy/plan_form.html", {"form": form, "program": plan.program})


@login_required
def milestone_add(request, plan_pk):
    plan = get_object_or_404(DevelopmentPlan, pk=plan_pk)
    form = MilestoneForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ms = form.save(commit=False)
        ms.plan = plan
        ms.save()
        messages.success(request, _("Milestone added."))
    return redirect("academy:plan_detail", pk=plan_pk)


@login_required
def milestone_toggle(request, pk):
    ms = get_object_or_404(DevelopmentMilestone, pk=pk)
    from django.utils import timezone
    ms.achieved = not ms.achieved
    ms.achieved_date = timezone.now().date() if ms.achieved else None
    ms.save(update_fields=["achieved", "achieved_date"])
    return redirect("academy:plan_detail", pk=ms.plan.pk)
