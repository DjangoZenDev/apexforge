"""
Videos — Match / training video library with timestamp notes and tagging
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class VideoCategory(models.Model):
    class CategoryType(models.TextChoices):
        MATCH     = "match",     _("Match Analysis")
        TRAINING  = "training",  _("Training Session")
        HIGHLIGHT = "highlight", _("Highlights")
        TACTICS   = "tactics",   _("Tactical Board")
        INTERVIEW = "interview", _("Interview")
        OTHER     = "other",     _("Other")

    name        = models.CharField(max_length=20, choices=CategoryType.choices, unique=True)
    icon        = models.CharField(max_length=10, default="🎬")
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name_plural = _("Video Categories")

    def __str__(self):
        return self.get_name_display()


class Video(models.Model):
    title       = models.CharField(max_length=255)
    category    = models.ForeignKey(VideoCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="videos")
    team        = models.ForeignKey("teams.Team", on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="videos")
    description = models.TextField(blank=True)
    video_file  = models.FileField(upload_to="videos/files/", null=True, blank=True)
    video_url   = models.URLField(blank=True, help_text=_("YouTube / Vimeo URL"))
    thumbnail   = models.ImageField(upload_to="videos/thumbs/", null=True, blank=True)
    date        = models.DateField()
    duration_sec= models.PositiveIntegerField(null=True, blank=True)
    tags        = models.CharField(max_length=500, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                    related_name="uploaded_videos")
    is_public   = models.BooleanField(default=False)
    views       = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def duration_display(self):
        if not self.duration_sec:
            return "—"
        h = self.duration_sec // 3600
        m = (self.duration_sec % 3600) // 60
        s = self.duration_sec % 60
        return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    @property
    def embed_url(self):
        url = self.video_url
        if not url:
            return None
        if "youtube.com/watch" in url:
            return f"https://www.youtube.com/embed/{url.split('v=')[-1].split('&')[0]}"
        if "youtu.be/" in url:
            return f"https://www.youtube.com/embed/{url.split('youtu.be/')[-1].split('?')[0]}"
        if "vimeo.com/" in url:
            return f"https://player.vimeo.com/video/{url.split('vimeo.com/')[-1].split('?')[0]}"
        return url


class VideoNote(models.Model):
    class NoteType(models.TextChoices):
        TACTICAL    = "tactical",    _("Tactical")
        TECHNICAL   = "technical",   _("Technical")
        POSITIVE    = "positive",    _("Positive Moment")
        IMPROVEMENT = "improvement", _("Area to Improve")
        INCIDENT    = "incident",    _("Incident")
        OTHER       = "other",       _("Other")

    video          = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="notes")
    timestamp_sec  = models.PositiveIntegerField(default=0)
    note_text      = models.TextField()
    note_type      = models.CharField(max_length=20, choices=NoteType.choices, default=NoteType.TACTICAL)
    tagged_players = models.ManyToManyField("players.Player", blank=True, related_name="video_notes")
    created_by     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp_sec"]

    def __str__(self):
        return f"{self.video} @ {self.timestamp_display}"

    @property
    def timestamp_display(self):
        m = self.timestamp_sec // 60
        s = self.timestamp_sec % 60
        return f"{m:02d}:{s:02d}"
