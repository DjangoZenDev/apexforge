"""
Inventory — Equipment, kit, gear stock tracking with low-stock alerts
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ItemCategory(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    icon        = models.CharField(max_length=10, default="📦")
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering            = ["name"]
        verbose_name_plural = _("Item Categories")

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    name         = models.CharField(max_length=200)
    sku          = models.CharField(max_length=50, unique=True)
    category     = models.ForeignKey(ItemCategory, on_delete=models.SET_NULL, null=True, related_name="items")
    description  = models.TextField(blank=True)
    quantity     = models.PositiveIntegerField(default=0)
    min_quantity = models.PositiveIntegerField(default=5, help_text=_("Low-stock alert threshold"))
    unit_price   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier     = models.CharField(max_length=200, blank=True)
    location     = models.CharField(max_length=200, blank=True)
    image        = models.ImageField(upload_to="inventory/", null=True, blank=True)
    team         = models.ForeignKey("teams.Team", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="inventory_items")
    notes        = models.TextField(blank=True)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_quantity

    @property
    def total_value(self):
        return self.quantity * self.unit_price


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        IN         = "in",         _("Stock In")
        OUT        = "out",        _("Stock Out")
        ADJUSTMENT = "adjustment", _("Adjustment")
        TRANSFER   = "transfer",   _("Transfer")

    item          = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    quantity      = models.IntegerField()
    date          = models.DateField(auto_now_add=True)
    reference     = models.CharField(max_length=100, blank=True)
    notes         = models.CharField(max_length=255, blank=True)
    performed_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        sign = "+" if self.quantity >= 0 else ""
        return f"{self.item} {sign}{self.quantity}"


class KitAssignment(models.Model):
    class Condition(models.TextChoices):
        NEW  = "new",  _("New")
        GOOD = "good", _("Good")
        FAIR = "fair", _("Fair")
        POOR = "poor", _("Poor")

    item               = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="assignments")
    assigned_to_player = models.ForeignKey("players.Player", on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name="kit_assignments")
    assigned_to_user   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name="kit_assignments")
    quantity           = models.PositiveSmallIntegerField(default=1)
    assigned_date      = models.DateField()
    expected_return    = models.DateField(null=True, blank=True)
    actual_return      = models.DateField(null=True, blank=True)
    condition_issued   = models.CharField(max_length=10, choices=Condition.choices, default=Condition.GOOD)
    condition_returned = models.CharField(max_length=10, choices=Condition.choices, null=True, blank=True)
    notes              = models.CharField(max_length=255, blank=True)
    is_returned        = models.BooleanField(default=False)

    class Meta:
        ordering = ["-assigned_date"]

    def __str__(self):
        recipient = self.assigned_to_player or self.assigned_to_user
        return f"{self.item.name} → {recipient}"
