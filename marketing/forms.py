from django import forms
from .models import NewsPost, Announcement, Campaign


class NewsPostForm(forms.ModelForm):
    publish_now = forms.BooleanField(required=False, label="Publish immediately")

    class Meta:
        model = NewsPost
        fields = [
            "title", "slug", "category", "content", "excerpt",
            "hero_image", "is_featured", "tags",
        ]
        widgets = {
            "title":      forms.TextInput(attrs={"class": "form-input"}),
            "slug":       forms.TextInput(attrs={"class": "form-input"}),
            "category":   forms.Select(attrs={"class": "form-select"}),
            "content":    forms.Textarea(attrs={"class": "form-input", "rows": 12}),
            "excerpt":    forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "hero_image": forms.FileInput(attrs={"class": "form-input"}),
            "tags":       forms.TextInput(attrs={"class": "form-input", "placeholder": "tag1, tag2, ..."}),
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        exclude = ["created_by"]
        widgets = {
            "title":        forms.TextInput(attrs={"class": "form-input"}),
            "message":      forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "level":        forms.Select(attrs={"class": "form-select"}),
            "target_roles": forms.TextInput(attrs={"class": "form-input"}),
            "expires_at":   forms.DateTimeInput(attrs={"class": "form-input", "type": "datetime-local"}),
        }


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        exclude = ["created_by", "impressions", "clicks", "conversions", "revenue"]
        widgets = {
            "name":        forms.TextInput(attrs={"class": "form-input"}),
            "channel":     forms.Select(attrs={"class": "form-select"}),
            "status":      forms.Select(attrs={"class": "form-select"}),
            "objective":   forms.TextInput(attrs={"class": "form-input"}),
            "budget":      forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "start_date":  forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "end_date":    forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }
