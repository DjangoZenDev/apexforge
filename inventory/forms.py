from django import forms
from django.utils.translation import gettext_lazy as _
from .models import InventoryItem, StockMovement, KitAssignment


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ["name", "sku", "category", "description", "quantity", "min_quantity",
                  "unit_price", "supplier", "location", "image", "team", "notes"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ["movement_type", "quantity", "reference", "notes"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": "1"}),
        }


class KitAssignmentForm(forms.ModelForm):
    class Meta:
        model = KitAssignment
        fields = ["assigned_to_player", "assigned_to_user", "quantity",
                  "assigned_date", "expected_return", "condition_issued", "notes"]
        widgets = {
            "assigned_date": forms.DateInput(attrs={"type": "date"}),
            "expected_return": forms.DateInput(attrs={"type": "date"}),
        }
