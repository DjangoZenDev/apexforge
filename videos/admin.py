from django.contrib import admin
from .models import VideoCategory, Video, VideoNote


@admin.register(VideoCategory)
class VideoCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "icon"]


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "team", "date", "is_public", "views"]
    list_filter = ["category", "is_public", "team"]
    search_fields = ["title", "tags"]


@admin.register(VideoNote)
class VideoNoteAdmin(admin.ModelAdmin):
    list_display = ["video", "timestamp_display", "note_type", "created_by"]
    list_filter = ["note_type"]
