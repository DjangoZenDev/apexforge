"""
Accounts models — Custom User with role-based access control
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("Email address is required"))
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.SUPER_ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        SUPER_ADMIN   = "super_admin",   _("Super Admin")
        CLUB_OWNER    = "club_owner",    _("Club Owner / Entrepreneur")
        MANAGER       = "manager",       _("Manager")
        COACH         = "coach",         _("Coach")
        ATHLETE       = "athlete",       _("Athlete / Player")
        SCOUT         = "scout",         _("Scout")
        FAN_INVESTOR  = "fan_investor",  _("Fan / Investor")

    email      = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name  = models.CharField(_("last name"),  max_length=150, blank=True)
    role       = models.CharField(_("role"), max_length=30, choices=Role.choices, default=Role.FAN_INVESTOR)
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["email"]

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    # ── Role helpers ──────────────────────────────────────────────────────────
    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN

    @property
    def is_club_owner(self):
        return self.role == self.Role.CLUB_OWNER

    @property
    def is_manager(self):
        return self.role == self.Role.MANAGER

    @property
    def is_coach(self):
        return self.role == self.Role.COACH

    @property
    def is_athlete(self):
        return self.role == self.Role.ATHLETE

    @property
    def is_scout(self):
        return self.role == self.Role.SCOUT

    @property
    def is_fan_investor(self):
        return self.role == self.Role.FAN_INVESTOR

    @property
    def can_manage(self):
        return self.role in (
            self.Role.SUPER_ADMIN,
            self.Role.CLUB_OWNER,
            self.Role.MANAGER,
        )


class UserProfile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar      = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio         = models.TextField(blank=True)
    phone       = models.CharField(max_length=30, blank=True)
    nationality = models.CharField(max_length=60, blank=True)
    city        = models.CharField(max_length=100, blank=True)
    country     = models.CharField(max_length=100, blank=True)
    website     = models.URLField(blank=True)
    twitter     = models.CharField(max_length=100, blank=True)
    instagram   = models.CharField(max_length=100, blank=True)
    linkedin    = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    preferred_language = models.CharField(max_length=10, default="en")
    dark_mode   = models.BooleanField(default=False)
    notifications_email = models.BooleanField(default=True)
    notifications_web   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")

    def __str__(self):
        return f"Profile — {self.user}"

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return "/static/img/default-avatar.svg"


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
