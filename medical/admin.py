from django.contrib import admin
from .models import Injury, RecoveryPlan, Treatment, MedicalRecord


class TreatmentInline(admin.TabularInline):
    model = Treatment
    extra = 0


@admin.register(Injury)
class InjuryAdmin(admin.ModelAdmin):
    list_display = ["player", "injury_type", "body_part", "severity", "status", "injury_date"]
    list_filter = ["status", "severity", "body_part"]
    search_fields = ["player__first_name", "player__last_name", "injury_type"]
    inlines = [TreatmentInline]


@admin.register(RecoveryPlan)
class RecoveryPlanAdmin(admin.ModelAdmin):
    list_display = ["injury", "start_date", "target_date", "physio_name"]


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ["player", "record_type", "date", "physician", "is_confidential"]
    list_filter = ["record_type", "is_confidential"]
