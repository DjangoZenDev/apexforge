from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Contract, ContractClause


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ["title", "contract_type", "party_name", "party_email", "party_phone",
                  "player", "team", "start_date", "end_date", "value", "currency",
                  "status", "file", "signed_date", "auto_renew", "renewal_notice_days", "notes"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "signed_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class ContractClauseForm(forms.ModelForm):
    class Meta:
        model = ContractClause
        fields = ["clause_type", "title", "description", "is_key_clause", "order"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
