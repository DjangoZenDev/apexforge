"""
Contracts — Player contracts, sponsorship agreements, staff contracts
"""
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Contract(models.Model):
    class ContractType(models.TextChoices):
        PLAYER      = "player",      _("Player Contract")
        STAFF       = "staff",       _("Staff Contract")
        SPONSORSHIP = "sponsorship", _("Sponsorship Agreement")
        VENDOR      = "vendor",      _("Vendor Contract")
        FACILITY    = "facility",    _("Facility Lease")
        OTHER       = "other",       _("Other")

    class Status(models.TextChoices):
        DRAFT      = "draft",      _("Draft")
        ACTIVE     = "active",     _("Active")
        EXPIRED    = "expired",    _("Expired")
        TERMINATED = "terminated", _("Terminated")
        RENEWED    = "renewed",    _("Renewed")

    class Currency(models.TextChoices):
        EUR = "EUR", "EUR €"
        USD = "USD", "USD $"
        GBP = "GBP", "GBP £"

    title               = models.CharField(max_length=255)
    contract_type       = models.CharField(max_length=20, choices=ContractType.choices)
    party_name          = models.CharField(max_length=200)
    party_email         = models.EmailField(blank=True)
    party_phone         = models.CharField(max_length=30, blank=True)
    player              = models.ForeignKey("players.Player", on_delete=models.SET_NULL,
                                            null=True, blank=True, related_name="contracts")
    team                = models.ForeignKey("teams.Team", on_delete=models.SET_NULL,
                                            null=True, blank=True, related_name="contracts")
    start_date          = models.DateField()
    end_date            = models.DateField()
    value               = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    currency            = models.CharField(max_length=3, choices=Currency.choices, default=Currency.EUR)
    status              = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    file                = models.FileField(upload_to="contracts/", null=True, blank=True)
    signed_date         = models.DateField(null=True, blank=True)
    signed_by           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                            null=True, blank=True, related_name="signed_contracts")
    auto_renew          = models.BooleanField(default=False)
    renewal_notice_days = models.PositiveSmallIntegerField(default=30)
    notes               = models.TextField(blank=True)
    created_by          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                            null=True, related_name="created_contracts")
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.party_name})"

    @property
    def is_expiring_soon(self):
        days_left = (self.end_date - timezone.now().date()).days
        return 0 <= days_left <= self.renewal_notice_days

    @property
    def days_remaining(self):
        return (self.end_date - timezone.now().date()).days


class ContractClause(models.Model):
    class ClauseType(models.TextChoices):
        PERFORMANCE  = "performance",  _("Performance Clause")
        BONUS        = "bonus",        _("Bonus Clause")
        PENALTY      = "penalty",      _("Penalty Clause")
        CONFIDENTIAL = "confidential", _("Confidentiality")
        TERMINATION  = "termination",  _("Termination")
        RENEWAL      = "renewal",      _("Renewal Option")
        OTHER        = "other",        _("Other")

    contract      = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="clauses")
    clause_type   = models.CharField(max_length=20, choices=ClauseType.choices)
    title         = models.CharField(max_length=200)
    description   = models.TextField()
    is_key_clause = models.BooleanField(default=False)
    order         = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.contract} — {self.title}"
