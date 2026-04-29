"""
Organizations — Multi-club management
"""
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Organization(models.Model):
    name          = models.CharField(max_length=150)
    slug          = models.SlugField(unique=True, blank=True)
    logo          = models.ImageField(upload_to="organizations/logos/", null=True, blank=True)
    country       = models.CharField(max_length=80, blank=True)
    website       = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    description   = models.TextField(blank=True)
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def club_count(self):
        return self.clubs.filter(is_active=True).count()


class Club(models.Model):
    organization  = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="clubs"
    )
    name          = models.CharField(max_length=150)
    city          = models.CharField(max_length=100, blank=True)
    country       = models.CharField(max_length=80, blank=True)
    stadium       = models.CharField(max_length=150, blank=True)
    stadium_capacity = models.PositiveIntegerField(null=True, blank=True)
    founded_year  = models.PositiveSmallIntegerField(null=True, blank=True)
    contact_email = models.EmailField(blank=True)
    phone         = models.CharField(max_length=30, blank=True)
    logo          = models.ImageField(upload_to="organizations/club_logos/", null=True, blank=True)
    colors        = models.CharField(max_length=100, blank=True, help_text=_("e.g. Red & White"))
    website       = models.URLField(blank=True)
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.organization})"

    @property
    def member_count(self):
        return self.user_accesses.count()


class UserClubAccess(models.Model):
    class Role(models.TextChoices):
        OWNER   = "owner",   _("Owner")
        ADMIN   = "admin",   _("Admin")
        MANAGER = "manager", _("Manager")
        COACH   = "coach",   _("Coach")
        ANALYST = "analyst", _("Analyst")
        VIEWER  = "viewer",  _("Viewer")

    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="club_accesses"
    )
    club       = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="user_accesses"
    )
    role       = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)
    is_primary = models.BooleanField(
        default=False, help_text=_("Default club shown when user logs in")
    )
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="granted_club_accesses"
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "club")]
        ordering = ["-is_primary", "role"]

    def __str__(self):
        return f"{self.user} → {self.club} ({self.get_role_display()})"
