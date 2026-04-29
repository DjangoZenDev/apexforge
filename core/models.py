"""
Core models — ActivityLog, Notification, ClubBranding, GlobalSearch
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ClubBranding(models.Model):
    """Singleton-ish model for club identity & branding."""
    name            = models.CharField(_("club name"), max_length=200, default="ApexForge FC")
    tagline         = models.CharField(max_length=300, blank=True)
    logo            = models.ImageField(upload_to="branding/", blank=True, null=True)
    primary_color   = models.CharField(max_length=7, default="#059669")   # emerald-600
    secondary_color = models.CharField(max_length=7, default="#f59e0b")   # amber-500
    founded_year    = models.PositiveSmallIntegerField(null=True, blank=True)
    city            = models.CharField(max_length=100, blank=True)
    country         = models.CharField(max_length=100, blank=True)
    website         = models.URLField(blank=True)
    email           = models.EmailField(blank=True)
    phone           = models.CharField(max_length=30, blank=True)
    twitter         = models.CharField(max_length=100, blank=True)
    instagram       = models.CharField(max_length=100, blank=True)
    facebook        = models.CharField(max_length=100, blank=True)
    youtube         = models.CharField(max_length=100, blank=True)
    tiktok          = models.CharField(max_length=100, blank=True)
    linkedin        = models.CharField(max_length=100, blank=True)
    discord         = models.CharField(max_length=100, blank=True)
    twitch          = models.CharField(max_length=100, blank=True)
    description     = models.TextField(blank=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("club branding")

    def __str__(self):
        return self.name

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ActivityLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "create", _("Created")
        UPDATE = "update", _("Updated")
        DELETE = "delete", _("Deleted")
        LOGIN  = "login",  _("Logged In")
        LOGOUT = "logout", _("Logged Out")
        VIEW   = "view",   _("Viewed")
        EXPORT = "export", _("Exported")
        IMPORT = "import", _("Imported")
        OTHER  = "other",  _("Other")

    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="activity_logs",
    )
    action      = models.CharField(max_length=20, choices=Action.choices, default=Action.OTHER)
    description = models.TextField()
    model_name  = models.CharField(max_length=100, blank=True)
    object_id   = models.PositiveIntegerField(null=True, blank=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    user_agent  = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("activity log")
        verbose_name_plural = _("activity logs")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user} — {self.action} — {self.created_at:%Y-%m-%d %H:%M}"

    @classmethod
    def log(cls, user, action, description, model_name="", object_id=None,
            ip_address=None, user_agent=""):
        return cls.objects.create(
            user=user, action=action, description=description,
            model_name=model_name, object_id=object_id,
            ip_address=ip_address, user_agent=user_agent,
        )


class Notification(models.Model):
    class Level(models.TextChoices):
        INFO    = "info",    _("Info")
        SUCCESS = "success", _("Success")
        WARNING = "warning", _("Warning")
        ERROR   = "error",   _("Error")

    recipient   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="notifications",
    )
    title       = models.CharField(max_length=200)
    message     = models.TextField()
    level       = models.CharField(max_length=10, choices=Level.choices, default=Level.INFO)
    link        = models.CharField(max_length=500, blank=True)
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient} — {self.title}"

    @classmethod
    def notify(cls, recipient, title, message, level=Level.INFO, link=""):
        return cls.objects.create(
            recipient=recipient, title=title, message=message,
            level=level, link=link,
        )


class ContactMessage(models.Model):
    """Public contact-form submissions."""
    SUBJECT_CHOICES = [
        ("general",  _("General Enquiry")),
        ("support",  _("Technical Support")),
        ("orders",   _("Orders & Payments")),
        ("tickets",  _("Tickets & Events")),
        ("account",  _("Account & Profile")),
        ("press",    _("Press & Media")),
        ("other",    _("Other")),
    ]
    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100)
    email       = models.EmailField()
    subject     = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default="general")
    message     = models.TextField()
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = _("contact message")
        verbose_name_plural = _("contact messages")
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}> — {self.get_subject_display()}"
