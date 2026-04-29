from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Video, VideoNote


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ["title", "category", "team", "description", "video_file", "video_url",
                  "thumbnail", "date", "duration_sec", "tags", "is_public"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "tags": forms.TextInput(attrs={"placeholder": "tag1, tag2, tag3"}),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("video_file") and not cleaned.get("video_url"):
            raise forms.ValidationError(_("Please upload a video file or provide a URL."))
        return cleaned


class VideoNoteForm(forms.ModelForm):
    class Meta:
        model = VideoNote
        fields = ["timestamp_sec", "note_text", "note_type", "tagged_players"]
        widgets = {
            "note_text": forms.Textarea(attrs={"rows": 2, "placeholder": "Add a note at this timestamp..."}),
            "tagged_players": forms.CheckboxSelectMultiple(),
            "timestamp_sec": forms.NumberInput(attrs={"min": "0", "placeholder": "Seconds (e.g. 125 = 2:05)"}),
        }
