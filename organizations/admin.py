from django.contrib import admin
from .models import Organization, Club, UserClubAccess


class ClubInline(admin.TabularInline):
    model = Club
    extra = 0
    fields = ["name", "city", "founded_year", "is_active"]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "club_count", "is_active", "created_at"]
    list_filter  = ["is_active", "country"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ClubInline]


class AccessInline(admin.TabularInline):
    model = UserClubAccess
    extra = 0
    fields = ["user", "role", "is_primary"]


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display  = ["name", "organization", "city", "founded_year", "is_active"]
    list_filter   = ["is_active", "organization"]
    search_fields = ["name", "city"]
    inlines = [AccessInline]


@admin.register(UserClubAccess)
class UserClubAccessAdmin(admin.ModelAdmin):
    list_display = ["user", "club", "role", "is_primary", "granted_at"]
    list_filter  = ["role"]
