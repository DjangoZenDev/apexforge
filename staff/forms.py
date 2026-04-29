from django import forms
from django.utils.translation import gettext_lazy as _
from .models import StaffMember, Task, Payroll


class StaffMemberForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = ["user", "department", "job_title", "employment_type", "hire_date",
                  "contract_end", "salary", "phone", "emergency_contact", "team", "bio"]
        widgets = {
            "hire_date": forms.DateInput(attrs={"type": "date"}),
            "contract_end": forms.DateInput(attrs={"type": "date"}),
            "bio": forms.Textarea(attrs={"rows": 3}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "assigned_to", "due_date", "status", "priority", "team", "notes"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ["staff_member", "period_start", "period_end",
                  "gross_salary", "deductions", "bonuses", "paid_date", "is_paid", "notes"]
        widgets = {
            "period_start": forms.DateInput(attrs={"type": "date"}),
            "period_end": forms.DateInput(attrs={"type": "date"}),
            "paid_date": forms.DateInput(attrs={"type": "date"}),
        }
