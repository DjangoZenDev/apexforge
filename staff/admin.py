from django.contrib import admin
from .models import Department, StaffMember, Task, Payroll


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "icon"]


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ["user", "job_title", "department", "employment_type", "hire_date", "is_active"]
    list_filter = ["department", "employment_type", "is_active"]
    search_fields = ["user__first_name", "user__last_name", "job_title"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "assigned_to", "due_date", "status", "priority"]
    list_filter = ["status", "priority"]
    search_fields = ["title"]


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ["staff_member", "period_start", "period_end", "gross_salary", "net_salary", "is_paid"]
    list_filter = ["is_paid"]
