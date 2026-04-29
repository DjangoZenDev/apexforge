from django.contrib import admin
from .models import NewsPost, Announcement, Campaign, SponsorPortal


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display  = ("title", "category", "author", "is_published", "is_featured", "views", "published_at")
    list_filter   = ("category", "is_published", "is_featured")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    actions = ["publish_posts"]

    def publish_posts(self, request, queryset):
        for post in queryset:
            post.publish()
        self.message_user(request, f"Published {queryset.count()} posts.")
    publish_posts.short_description = "Publish selected posts"


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "level", "is_active", "created_at")
    list_filter  = ("level", "is_active")


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "channel", "status", "budget", "impressions", "clicks")
    list_filter  = ("channel", "status")


@admin.register(SponsorPortal)
class SponsorPortalAdmin(admin.ModelAdmin):
    list_display = ("sponsorship", "tier", "is_visible", "display_order")
    list_editable = ("is_visible", "display_order")
