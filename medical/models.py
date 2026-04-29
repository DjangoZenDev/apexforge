"""
Medical — Injury tracking, recovery plans, treatments, medical records
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class BodyPart(models.TextChoices):
    HEAD     = "head",     _("Head")
    NECK     = "neck",     _("Neck")
    SHOULDER = "shoulder", _("Shoulder")
    ARM      = "arm",      _("Arm")
    ELBOW    = "elbow",    _("Elbow")
    WRIST    = "wrist",    _("Wrist")
    CHEST    = "chest",    _("Chest")
    BACK     = "back",     _("Back")
    HIP      = "hip",      _("Hip")
    GROIN    = "groin",    _("Groin")
    THIGH    = "thigh",    _("Thigh")
    KNEE     = "knee",     _("Knee")
    SHIN     = "shin",     _("Shin")
    ANKLE    = "ankle",    _("Ankle")
    FOOT     = "foot",     _("Foot")
    OTHER    = "other",    _("Other")


class Injury(models.Model):
    class Severity(models.TextChoices):
        MINOR    = "minor",    _("Minor (< 7 days)")
        MODERATE = "moderate", _("Moderate (1–4 weeks)")
        SEVERE   = "severe",   _("Severe (1–3 months)")
        CRITICAL = "critical", _("Critical (3+ months)")

    class Status(models.TextChoices):
        ACTIVE     = "active",     _("Active")
        RECOVERING = "recovering", _("Recovering")
        RECOVERED  = "recovered",  _("Recovered")

    player            = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="medical_injuries")
    injury_type       = models.CharField(max_length=120)
    body_part         = models.CharField(max_length=30, choices=BodyPart.choices)
    severity          = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MINOR)
    status            = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    injury_date       = models.DateField()
    expected_recovery = models.DateField(null=True, blank=True)
    actual_recovery   = models.DateField(null=True, blank=True)
    mechanism         = models.CharField(max_length=200, blank=True, help_text=_("How the injury happened"))
    description       = models.TextField(blank=True)
    reported_by       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                          null=True, related_name="reported_injuries")
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering            = ["-injury_date"]
        verbose_name_plural = _("Injuries")

    def __str__(self):
        return f"{self.player} — {self.injury_type} ({self.get_status_display()})"

    @property
    def days_out(self):
        from django.utils import timezone
        end = self.actual_recovery or timezone.now().date()
        return (end - self.injury_date).days


class RecoveryPlan(models.Model):
    injury         = models.OneToOneField(Injury, on_delete=models.CASCADE, related_name="recovery_plan")
    plan_details   = models.TextField()
    start_date     = models.DateField()
    target_date    = models.DateField()
    physio_name    = models.CharField(max_length=120, blank=True)
    milestones     = models.TextField(blank=True, help_text=_("Newline-separated milestones"))
    progress_notes = models.TextField(blank=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recovery plan — {self.injury}"


class Treatment(models.Model):
    class TreatmentType(models.TextChoices):
        PHYSIO     = "physio",     _("Physiotherapy")
        MASSAGE    = "massage",    _("Massage")
        ICE        = "ice",        _("Ice / Cold Therapy")
        SURGERY    = "surgery",    _("Surgery")
        MEDICATION = "medication", _("Medication")
        REST       = "rest",       _("Rest")
        GYM        = "gym",        _("Gym Rehabilitation")
        OTHER      = "other",      _("Other")

    injury         = models.ForeignKey(Injury, on_delete=models.CASCADE, related_name="treatments")
    treatment_type = models.CharField(max_length=20, choices=TreatmentType.choices)
    date           = models.DateField()
    practitioner   = models.CharField(max_length=120, blank=True)
    notes          = models.TextField(blank=True)
    next_session   = models.DateField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.get_treatment_type_display()} on {self.date}"


class MedicalRecord(models.Model):
    class RecordType(models.TextChoices):
        PHYSICAL     = "physical",     _("Physical Exam")
        BLOOD_TEST   = "blood_test",   _("Blood Test")
        VACCINATION  = "vaccination",  _("Vaccination")
        IMAGING      = "imaging",      _("Imaging (X-ray/MRI/CT)")
        PRESCRIPTION = "prescription", _("Prescription")
        OTHER        = "other",        _("Other")

    player          = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="medical_records")
    record_type     = models.CharField(max_length=20, choices=RecordType.choices)
    date            = models.DateField()
    description     = models.TextField()
    physician       = models.CharField(max_length=120, blank=True)
    facility        = models.CharField(max_length=200, blank=True)
    file            = models.FileField(upload_to="medical/records/", null=True, blank=True)
    is_confidential = models.BooleanField(default=True)
    created_by      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                        null=True, related_name="created_medical_records")
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.player} — {self.get_record_type_display()} ({self.date})"
