"""Performance Insights — analytics dashboard"""
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Max, Sum, Q
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


@login_required
def dashboard(request):
    """Main analytics dashboard — aggregates data from all apps."""
    today = timezone.now().date()
    current_year = today.year

    # ── Players ──────────────────────────────────────────────────────────────
    from players.models import Player, PlayerStats
    player_status = dict(
        Player.objects.values("status").annotate(n=Count("id")).values_list("status", "n")
    )
    top_scorers = (
        PlayerStats.objects.select_related("player", "season")
        .filter(goals__gt=0)
        .order_by("-goals")[:10]
    )
    top_assisters = (
        PlayerStats.objects.select_related("player", "season")
        .filter(assists__gt=0)
        .order_by("-assists")[:10]
    )
    avg_rating = PlayerStats.objects.filter(rating__isnull=False).aggregate(
        avg=Avg("rating")
    )["avg"]

    # ── Medical / Injuries ────────────────────────────────────────────────────
    from medical.models import Injury
    injury_by_status = dict(
        Injury.objects.values("status").annotate(n=Count("id")).values_list("status", "n")
    )
    injury_by_severity = dict(
        Injury.objects.values("severity").annotate(n=Count("id")).values_list("severity", "n")
    )
    active_injuries = Injury.objects.filter(
        status__in=["active", "recovering"]
    ).select_related("player").order_by("-injury_date")[:5]

    # ── Tournaments / Matches ─────────────────────────────────────────────────
    from tournaments.models import Match
    match_totals = Match.objects.aggregate(
        total=Count("id"),
        completed=Count("id", filter=Q(status="completed")),
        home_wins=Count("id", filter=Q(
            status="completed",
            home_score__gt=0,
        )),
    )
    recent_matches = Match.objects.filter(
        status="completed"
    ).select_related("home_team", "away_team").order_by("-date")[:8]

    # ── Finance ───────────────────────────────────────────────────────────────
    try:
        from finance.models import Transaction
        finance_summary = Transaction.objects.filter(
            date__year=current_year
        ).aggregate(
            income=Sum("amount", filter=Q(transaction_type="income")),
            expense=Sum("amount", filter=Q(transaction_type="expense")),
        )
        finance_income = finance_summary["income"] or 0
        finance_expense = finance_summary["expense"] or 0
    except Exception:
        finance_income = finance_expense = 0

    # ── Staff / Tasks ─────────────────────────────────────────────────────────
    from staff.models import Task, Payroll
    task_by_status = dict(
        Task.objects.values("status").annotate(n=Count("id")).values_list("status", "n")
    )
    overdue_tasks = Task.objects.filter(
        due_date__lt=today, status__in=["pending", "in_progress"]
    ).count()
    payroll_ytd = Payroll.objects.filter(
        period_start__year=current_year
    ).aggregate(total=Sum("net_salary"))["total"] or 0

    # ── Academy ───────────────────────────────────────────────────────────────
    from academy.models import DevelopmentPlan, AcademyProgram
    academy_programs = AcademyProgram.objects.filter(is_active=True).count()
    avg_overall = DevelopmentPlan.objects.filter(
        overall_rating__isnull=False
    ).aggregate(avg=Avg("overall_rating"))["avg"]

    # ── Contracts ────────────────────────────────────────────────────────────
    from contracts.models import Contract
    contract_stats = Contract.objects.aggregate(
        active=Count("id", filter=Q(status="active")),
        expiring=Count("id", filter=Q(
            status="active", end_date__lte=today + timezone.timedelta(days=60)
        )),
        expired=Count("id", filter=Q(status="expired")),
    )

    # ── Chart data (JSON-serialisable) ────────────────────────────────────────
    import json

    # Player status pie
    status_labels = list(player_status.keys())
    status_values = list(player_status.values())

    # Injury severity bar
    severity_labels = list(injury_by_severity.keys())
    severity_values = list(injury_by_severity.values())

    # Task status doughnut
    task_labels = list(task_by_status.keys())
    task_values = list(task_by_status.values())

    context = {
        # Players
        "player_status": player_status,
        "top_scorers": top_scorers,
        "top_assisters": top_assisters,
        "avg_rating": avg_rating,
        # Medical
        "injury_by_status": injury_by_status,
        "injury_by_severity": injury_by_severity,
        "active_injuries": active_injuries,
        # Tournaments
        "match_totals": match_totals,
        "recent_matches": recent_matches,
        # Finance
        "finance_income": finance_income,
        "finance_expense": finance_expense,
        "finance_balance": finance_income - finance_expense,
        # Staff
        "task_by_status": task_by_status,
        "overdue_tasks": overdue_tasks,
        "payroll_ytd": payroll_ytd,
        # Academy
        "academy_programs": academy_programs,
        "avg_overall": avg_overall,
        # Contracts
        "contract_stats": contract_stats,
        # Charts
        "chart_status_labels": json.dumps(status_labels),
        "chart_status_values": json.dumps(status_values),
        "chart_severity_labels": json.dumps(severity_labels),
        "chart_severity_values": json.dumps(severity_values),
        "chart_task_labels": json.dumps(task_labels),
        "chart_task_values": json.dumps(task_values),
    }
    return render(request, "insights/dashboard.html", context)
