from django import forms
from django.utils.translation import gettext_lazy as _
from .models import FanProfile, TicketCategory, Ticket, TicketPurchase, LoyaltyTransaction


class FanProfileForm(forms.ModelForm):
    class Meta:
        model = FanProfile
        fields = ["phone", "date_of_birth", "bio", "avatar", "favorite_player", "newsletter_opt_in"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "bio": forms.Textarea(attrs={"rows": 3}),
        }


class TicketCategoryForm(forms.ModelForm):
    class Meta:
        model = TicketCategory
        fields = ["name", "description", "base_price", "color", "perks", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "perks": forms.Textarea(attrs={"rows": 4, "placeholder": _("One perk per line")}),
        }


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["event", "category", "seat_row", "seat_number", "price", "status"]


class TicketBulkCreateForm(forms.Form):
    event     = forms.ModelChoiceField(
        queryset=None, label=_("Event"),
        widget=forms.Select(attrs={"class": "form-select w-full"})
    )
    category  = forms.ModelChoiceField(
        queryset=TicketCategory.objects.filter(is_active=True), label=_("Category"),
        widget=forms.Select(attrs={"class": "form-select w-full"})
    )
    quantity  = forms.IntegerField(min_value=1, max_value=5000, label=_("Number of tickets"))
    row_prefix = forms.CharField(max_length=5, required=False, label=_("Row prefix (e.g. A)"))
    price_override = forms.DecimalField(
        max_digits=8, decimal_places=2, required=False, label=_("Price override")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from events.models import Event
        self.fields["event"].queryset = Event.objects.filter(
            status="scheduled"
        ).order_by("start_date")


class LoyaltyAdjustForm(forms.Form):
    fan     = forms.ModelChoiceField(queryset=FanProfile.objects.all(), label=_("Fan"))
    points  = forms.IntegerField(label=_("Points (positive = add, negative = deduct)"))
    tx_type = forms.ChoiceField(choices=LoyaltyTransaction.TxType.choices, label=_("Type"))
    description = forms.CharField(max_length=200, label=_("Reason"))
