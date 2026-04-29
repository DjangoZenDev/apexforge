"""
Fans — Fan profiles, loyalty points, ticketing
"""
import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class MembershipTier(models.TextChoices):
    BRONZE   = "bronze",   _("Bronze")
    SILVER   = "silver",   _("Silver")
    GOLD     = "gold",     _("Gold")
    PLATINUM = "platinum", _("Platinum")


class FanProfile(models.Model):
    user            = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fan_profile"
    )
    phone           = models.CharField(max_length=30, blank=True)
    date_of_birth   = models.DateField(null=True, blank=True)
    bio             = models.TextField(blank=True)
    avatar          = models.ImageField(upload_to="fans/avatars/", null=True, blank=True)
    loyalty_points  = models.PositiveIntegerField(default=0)
    tier            = models.CharField(
        max_length=20, choices=MembershipTier.choices, default=MembershipTier.BRONZE
    )
    favorite_player = models.ForeignKey(
        "players.Player", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="fan_favourites"
    )
    newsletter_opt_in = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.get_tier_display()}"

    def recalculate_tier(self):
        pts = self.loyalty_points
        if pts >= 5000:
            tier = MembershipTier.PLATINUM
        elif pts >= 2000:
            tier = MembershipTier.GOLD
        elif pts >= 500:
            tier = MembershipTier.SILVER
        else:
            tier = MembershipTier.BRONZE
        if self.tier != tier:
            self.tier = tier
            self.save(update_fields=["tier"])

    @property
    def tier_progress(self):
        """Returns (current_pts, next_threshold, pct) for progress bar."""
        thresholds = [0, 500, 2000, 5000]
        pts = self.loyalty_points
        for i, t in enumerate(thresholds):
            if pts < t:
                prev = thresholds[i - 1]
                span = t - prev
                pct = min(100, int((pts - prev) / span * 100))
                return pts, t, pct
        return pts, 5000, 100  # Platinum maxed


class TicketCategory(models.Model):
    name        = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    base_price  = models.DecimalField(max_digits=8, decimal_places=2)
    color       = models.CharField(
        max_length=20, default="blue",
        help_text=_("Tailwind colour keyword: blue, amber, emerald, violet, red …")
    )
    perks       = models.TextField(blank=True, help_text=_("Newline-separated perks list"))
    is_active   = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = _("Ticket categories")
        ordering = ["base_price"]

    def __str__(self):
        return self.name

    @property
    def perks_list(self):
        return [p.strip() for p in self.perks.splitlines() if p.strip()]


class Ticket(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", _("Available")
        RESERVED  = "reserved",  _("Reserved")
        SOLD      = "sold",      _("Sold")
        USED      = "used",      _("Used")
        CANCELLED = "cancelled", _("Cancelled")

    event        = models.ForeignKey(
        "events.Event", on_delete=models.CASCADE,
        related_name="tickets", null=True, blank=True
    )
    category     = models.ForeignKey(
        TicketCategory, on_delete=models.PROTECT, related_name="tickets"
    )
    seat_row     = models.CharField(max_length=10, blank=True)
    seat_number  = models.CharField(max_length=10, blank=True)
    price        = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text=_("Leave blank to use category base price")
    )
    status       = models.CharField(
        max_length=20, choices=Status.choices, default=Status.AVAILABLE
    )
    owner        = models.ForeignKey(
        FanProfile, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="tickets"
    )
    purchased_at = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["event", "seat_row", "seat_number"]

    def __str__(self):
        seat = f"R{self.seat_row}-S{self.seat_number}" if self.seat_row else _("General")
        return f"{self.event} — {self.category} — {seat}"

    @property
    def effective_price(self):
        return self.price if self.price is not None else self.category.base_price


class TicketPurchase(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING  = "pending",  _("Pending")
        PAID     = "paid",     _("Paid")
        REFUNDED = "refunded", _("Refunded")
        FAILED   = "failed",   _("Failed")

    fan            = models.ForeignKey(
        FanProfile, on_delete=models.CASCADE, related_name="purchases"
    )
    tickets        = models.ManyToManyField(Ticket, related_name="purchase")
    total_amount   = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    loyalty_earned = models.PositiveIntegerField(default=0)
    reference      = models.CharField(max_length=16, unique=True, blank=True)
    notes          = models.TextField(blank=True)
    purchased_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-purchased_at"]

    def __str__(self):
        return f"#{self.reference} — {self.fan}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)


class LoyaltyTransaction(models.Model):
    class TxType(models.TextChoices):
        EARNED   = "earned",   _("Earned")
        REDEEMED = "redeemed", _("Redeemed")
        BONUS    = "bonus",    _("Bonus")
        EXPIRED  = "expired",  _("Expired")

    fan         = models.ForeignKey(
        FanProfile, on_delete=models.CASCADE, related_name="loyalty_transactions"
    )
    points      = models.IntegerField(help_text=_("Positive = earned, negative = spent/expired"))
    tx_type     = models.CharField(max_length=20, choices=TxType.choices)
    description = models.CharField(max_length=200)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.fan} {self.points:+} pts"
