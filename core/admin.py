from django.contrib import admin
from .models import ActivityLog, Notification, ClubBranding, ContactMessage


@admin.register(ClubBranding)
class ClubBrandingAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "country", "updated_at")


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display  = ("user", "action", "description", "created_at")
    list_filter   = ("action", "created_at")
    search_fields = ("user__email", "description", "model_name")
    readonly_fields = ("user", "action", "description", "model_name", "object_id",
                       "ip_address", "user_agent", "created_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ("recipient", "title", "level", "is_read", "created_at")
    list_filter   = ("level", "is_read")
    search_fields = ("recipient__email", "title")
    actions = ["mark_read"]

    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_read.short_description = "Mark selected as read"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ("first_name", "last_name", "email", "subject", "is_read", "created_at")
    list_filter   = ("subject", "is_read", "created_at")
    search_fields = ("first_name", "last_name", "email", "message")
    readonly_fields = ("first_name", "last_name", "email", "subject", "message",
                       "ip_address", "created_at")
    actions = ["mark_read"]
    date_hierarchy = "created_at"

    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_read.short_description = "Mark selected as read"
