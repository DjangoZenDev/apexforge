"""
Marketing models — News, Announcements, Campaigns, Sponsor Portal
"""
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class NewsPost(models.Model):
    class Category(models.TextChoices):
        CLUB      = "club",      _("Club News")
        MATCH     = "match",     _("Match Report")
        TRANSFER  = "transfer",  _("Transfer")
        YOUTH     = "youth",     _("Youth")
        COMMUNITY = "community", _("Community")
        SPONSOR   = "sponsor",   _("Sponsor")
        OTHER     = "other",     _("Other")

    title        = models.CharField(max_length=300)
    slug         = models.SlugField(unique=True, max_length=320)
    category     = models.CharField(max_length=20, choices=Category.choices, default=Category.CLUB)
    content      = models.TextField()
    excerpt      = models.TextField(max_length=500, blank=True)
    hero_image   = models.ImageField(upload_to="news/", blank=True, null=True)
    author       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="news_posts",
    )
    is_published  = models.BooleanField(default=False)
    published_at  = models.DateTimeField(null=True, blank=True)
    is_featured   = models.BooleanField(default=False)
    views         = models.PositiveIntegerField(default=0)
    tags          = models.CharField(max_length=300, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("news post")
        verbose_name_plural = _("news posts")
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("marketing:news_detail", kwargs={"slug": self.slug})

    def publish(self):
        self.is_published = True
        self.published_at = timezone.now()
        self.save(update_fields=["is_published", "published_at"])


class Announcement(models.Model):
    class Level(models.TextChoices):
        INFO    = "info",    _("Info")
        SUCCESS = "success", _("Success")
        WARNING = "warning", _("Warning")
        URGENT  = "urgent",  _("Urgent")

    title       = models.CharField(max_length=300)
    message     = models.TextField()
    level       = models.CharField(max_length=10, choices=Level.choices, default=Level.INFO)
    target_roles = models.CharField(max_length=200, blank=True, help_text=_("Comma-separated roles or blank for all"))
    is_active   = models.BooleanField(default=True)
    expires_at  = models.DateTimeField(null=True, blank=True)
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="announcements",
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("announcement")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        if self.expires_at:
            return self.expires_at < timezone.now()
        return False


class Campaign(models.Model):
    class Channel(models.TextChoices):
        EMAIL   = "email",   _("Email")
        SOCIAL  = "social",  _("Social Media")
        SMS     = "sms",     _("SMS")
        WEBSITE = "website", _("Website")
        OTHER   = "other",   _("Other")

    class Status(models.TextChoices):
        DRAFT   = "draft",   _("Draft")
        ACTIVE  = "active",  _("Active")
        PAUSED  = "paused",  _("Paused")
        ENDED   = "ended",   _("Ended")

    name         = models.CharField(max_length=200)
    channel      = models.CharField(max_length=20, choices=Channel.choices)
    status       = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    objective    = models.CharField(max_length=300, blank=True)
    budget       = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    start_date   = models.DateField(null=True, blank=True)
    end_date     = models.DateField(null=True, blank=True)
    description  = models.TextField(blank=True)
    # KPIs
    impressions  = models.PositiveIntegerField(default=0)
    clicks       = models.PositiveIntegerField(default=0)
    conversions  = models.PositiveIntegerField(default=0)
    revenue      = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="campaigns",
    )
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("campaign")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def ctr(self):
        if self.impressions:
            return round(self.clicks / self.impressions * 100, 2)
        return 0

    @property
    def conversion_rate(self):
        if self.clicks:
            return round(self.conversions / self.clicks * 100, 2)
        return 0

    @property
    def roi(self):
        if self.budget and float(self.budget) > 0 and self.revenue:
            return round((float(self.revenue) - float(self.budget)) / float(self.budget) * 100, 2)
        return None


class SponsorPortal(models.Model):
    """Public-facing sponsor portal entry."""
    sponsorship  = models.OneToOneField("finance.Sponsorship", on_delete=models.CASCADE, related_name="portal")
    tagline      = models.CharField(max_length=300, blank=True)
    description  = models.TextField(blank=True)
    is_visible   = models.BooleanField(default=True)
    tier         = models.CharField(max_length=50, blank=True, help_text=_("e.g. Gold, Silver, Bronze"))
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = _("sponsor portal")
        ordering = ["display_order"]

    def __str__(self):
        return f"Portal: {self.sponsorship}"
