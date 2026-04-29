"""Staff & HR views"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.decorators import staff_required, manager_required
from core.pdf import payroll_slip_pdf
from .models import StaffMember, Department, Task, Payroll
from .forms import StaffMemberForm, TaskForm, PayrollForm


@staff_required
def staff_list(request):
    qs = StaffMember.objects.select_related("user", "department", "team").filter(is_active=True)
    club = getattr(request, "active_club", None)
    if club:
        qs = qs.filter(team__club=club)
    dept = request.GET.get("dept")
    q = request.GET.get("q", "")
    if dept:
        qs = qs.filter(department_id=dept)
    if q:
        qs = qs.filter(
            Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) | Q(job_title__icontains=q)
        )
    departments = Department.objects.all()
    return render(request, "staff/list.html", {"staff": qs, "departments": departments})


@staff_required
def staff_detail(request, pk):
    member = get_object_or_404(StaffMember.objects.select_related("user", "department", "team"), pk=pk)
    tasks = Task.objects.filter(assigned_to=member.user).order_by("-created_at")[:10]
    payrolls = member.payrolls.order_by("-period_start")[:6]
    return render(request, "staff/detail.html", {"member": member, "tasks": tasks, "payrolls": payrolls})


@manager_required
def staff_create(request):
    form = StaffMemberForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Staff member added."))
        return redirect("staff:list")
    return render(request, "staff/form.html", {"form": form, "title": _("Add Staff Member")})


@manager_required
def staff_edit(request, pk):
    member = get_object_or_404(StaffMember, pk=pk)
    form = StaffMemberForm(request.POST or None, instance=member)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Staff member updated."))
        return redirect("staff:detail", pk=pk)
    return render(request, "staff/form.html", {"form": form, "title": _("Edit Staff Member"), "member": member})


@staff_required
def task_list(request):
    club = getattr(request, "active_club", None)
    if request.user.can_manage:
        qs = Task.objects.select_related("assigned_to", "assigned_by", "team").order_by("due_date")
        if club:
            qs = qs.filter(team__club=club)
    else:
        qs = Task.objects.filter(assigned_to=request.user).order_by("due_date")
    status = request.GET.get("status")
    priority = request.GET.get("priority")
    if status:
        qs = qs.filter(status=status)
    if priority:
        qs = qs.filter(priority=priority)
    # Auto-flag overdue tasks
    today = timezone.now().date()
    pending = qs.exclude(status__in=[Task.Status.COMPLETED, Task.Status.CANCELLED])
    overdue_count = sum(1 for t in pending if t.due_date < today)
    return render(request, "staff/tasks.html", {
        "tasks": qs,
        "overdue_count": overdue_count,
        "status_choices": Task.Status.choices,
        "priority_choices": Task.Priority.choices,
    })


@staff_required
def task_create(request):
    form = TaskForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        task.assigned_by = request.user
        task.save()
        messages.success(request, _("Task created."))
        return redirect("staff:tasks")
    return render(request, "staff/task_form.html", {"form": form, "title": _("New Task")})


@staff_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(request.POST or None, instance=task)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Task updated."))
        return redirect("staff:tasks")
    return render(request, "staff/task_form.html", {"form": form, "title": _("Edit Task"), "task": task})


@staff_required
def payroll_list(request):
    club = getattr(request, "active_club", None)
    if not request.user.can_manage:
        qs = Payroll.objects.filter(staff_member__user=request.user).order_by("-period_start")
    else:
        qs = Payroll.objects.select_related("staff_member__user").order_by("-period_start")
        if club:
            qs = qs.filter(staff_member__team__club=club)
    total_paid = qs.filter(is_paid=True).aggregate(t=Sum("net_salary"))["t"] or 0
    total_pending = qs.filter(is_paid=False).aggregate(t=Sum("net_salary"))["t"] or 0
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page", 1))
    return render(request, "staff/payroll.html", {
        "page": page, "total_paid": total_paid, "total_pending": total_pending,
    })


@manager_required
def payroll_create(request):
    form = PayrollForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Payroll entry created."))
        return redirect("staff:payroll")
    return render(request, "staff/payroll_form.html", {"form": form})


@staff_required
def payroll_pdf_view(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    return payroll_slip_pdf(payroll)
