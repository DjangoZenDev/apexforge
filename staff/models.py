"""
Staff & HR — Staff members, tasks, payroll
"""
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    icon        = models.CharField(max_length=10, default="🏢")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class StaffMember(models.Model):
    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", _("Full-Time")
        PART_TIME = "part_time", _("Part-Time")
        CONTRACT  = "contract",  _("Contract")
        VOLUNTEER = "volunteer", _("Volunteer")
        FREELANCE = "freelance", _("Freelance")

    user              = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                             related_name="staff_profile")
    department        = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name="members")
    job_title         = models.CharField(max_length=150)
    employment_type   = models.CharField(max_length=20, choices=EmploymentType.choices,
                                         default=EmploymentType.FULL_TIME)
    hire_date         = models.DateField()
    contract_end      = models.DateField(null=True, blank=True)
    salary            = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    phone             = models.CharField(max_length=30, blank=True)
    emergency_contact = models.CharField(max_length=200, blank=True)
    team              = models.ForeignKey("teams.Team", on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name="staff_members")
    bio               = models.TextField(blank=True)
    is_active         = models.BooleanField(default=True)

    class Meta:
        ordering = ["user__last_name"]

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.job_title}"


class Task(models.Model):
    class Status(models.TextChoices):
        PENDING     = "pending",     _("Pending")
        IN_PROGRESS = "in_progress", _("In Progress")
        COMPLETED   = "completed",   _("Completed")
        CANCELLED   = "cancelled",   _("Cancelled")

    class Priority(models.TextChoices):
        LOW    = "low",    _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH   = "high",   _("High")
        URGENT = "urgent", _("Urgent")

    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name="assigned_tasks")
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, related_name="created_tasks")
    due_date    = models.DateField()
    status      = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    priority    = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    team        = models.ForeignKey("teams.Team", on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="tasks")
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "-priority"]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        return (self.status not in (self.Status.COMPLETED, self.Status.CANCELLED)
                and self.due_date < timezone.now().date())


class Payroll(models.Model):
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name="payrolls")
    period_start = models.DateField()
    period_end   = models.DateField()
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    deductions   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonuses      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary   = models.DecimalField(max_digits=12, decimal_places=2)
    paid_date    = models.DateField(null=True, blank=True)
    is_paid      = models.BooleanField(default=False)
    notes        = models.CharField(max_length=255, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-period_start"]

    def __str__(self):
        return f"{self.staff_member} — {self.period_start:%b %Y}"

    def save(self, *args, **kwargs):
        self.net_salary = self.gross_salary + self.bonuses - self.deductions
        super().save(*args, **kwargs)
