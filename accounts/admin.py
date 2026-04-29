from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = _("Profile")
    fields = ("avatar", "bio", "phone", "nationality", "city", "country", "dark_mode")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display  = ("email", "get_full_name", "role", "is_active", "is_staff", "date_joined")
    list_filter   = ("role", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering      = ("-date_joined",)

    fieldsets = (
        (None,       {"fields": ("email", "password")}),
        (_("Personal"), {"fields": ("first_name", "last_name")}),
        (_("Role"),  {"fields": ("role",)}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Dates"),  {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "role", "password1", "password2"),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ("user", "city", "country", "dark_mode")
    search_fields = ("user__email", "city", "country")
