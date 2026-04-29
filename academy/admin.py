from django.contrib import admin
from .models import AcademyProgram, DevelopmentPlan, DevelopmentMilestone


class MilestoneInline(admin.TabularInline):
    model = DevelopmentMilestone
    extra = 0


@admin.register(AcademyProgram)
class AcademyProgramAdmin(admin.ModelAdmin):
    list_display = ["name", "age_group", "head_coach", "team", "is_active"]
    list_filter = ["age_group", "is_active"]


@admin.register(DevelopmentPlan)
class DevelopmentPlanAdmin(admin.ModelAdmin):
    list_display = ["player", "program", "season", "overall_rating", "updated_at"]
    list_filter = ["program", "season"]
    inlines = [MilestoneInline]
