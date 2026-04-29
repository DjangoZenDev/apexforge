"""
Finance models — Budget, Transactions, Sponsorships, Investments, Shop
"""
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class BudgetCategory(models.Model):
    name  = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#059669")

    class Meta:
        verbose_name = _("budget category")
        verbose_name_plural = _("budget categories")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Budget(models.Model):
    season   = models.ForeignKey("teams.Season", on_delete=models.CASCADE, related_name="budgets", null=True, blank=True)
    team     = models.ForeignKey("teams.Team", on_delete=models.SET_NULL, null=True, blank=True, related_name="budgets")
    category = models.ForeignKey(BudgetCategory, on_delete=models.SET_NULL, null=True, blank=True)
    name     = models.CharField(max_length=200)
    amount   = models.DecimalField(max_digits=14, decimal_places=2)
    notes    = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="budgets_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("budget")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — €{self.amount}"

    @property
    def spent(self):
        from django.db.models import Sum
        total = self.transactions.aggregate(t=Sum("amount"))["t"] or 0
        return total

    @property
    def remaining(self):
        return self.amount - self.spent


class Transaction(models.Model):
    class Type(models.TextChoices):
        INCOME  = "income",  _("Income")
        EXPENSE = "expense", _("Expense")

    class Status(models.TextChoices):
        PENDING   = "pending",   _("Pending")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    title            = models.CharField(max_length=200)
    transaction_type = models.CharField(max_length=10, choices=Type.choices)
    amount           = models.DecimalField(max_digits=14, decimal_places=2)
    date             = models.DateField()
    category         = models.ForeignKey(BudgetCategory, on_delete=models.SET_NULL, null=True, blank=True)
    budget           = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    team             = models.ForeignKey("teams.Team", on_delete=models.SET_NULL, null=True, blank=True)
    status           = models.CharField(max_length=15, choices=Status.choices, default=Status.COMPLETED)
    reference        = models.CharField(max_length=100, blank=True)
    notes            = models.TextField(blank=True)
    receipt          = models.FileField(upload_to="finance/receipts/", blank=True, null=True)
    created_by       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="transactions_created",
    )
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["-date"]),
            models.Index(fields=["transaction_type", "-date"]),
        ]

    def __str__(self):
        return f"{self.title} — €{self.amount} ({self.transaction_type})"


class Sponsorship(models.Model):
    class Type(models.TextChoices):
        SHIRT    = "shirt",    _("Shirt Sponsor")
        KIT      = "kit",      _("Kit Sponsor")
        STADIUM  = "stadium",  _("Stadium Sponsor")
        DIGITAL  = "digital",  _("Digital / Media")
        OFFICIAL = "official", _("Official Partner")
        OTHER    = "other",    _("Other")

    class Status(models.TextChoices):
        ACTIVE    = "active",    _("Active")
        EXPIRED   = "expired",   _("Expired")
        PENDING   = "pending",   _("Pending")
        CANCELLED = "cancelled", _("Cancelled")

    club          = models.ForeignKey(
        "organizations.Club", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sponsorships", verbose_name=_("club"),
    )
    company_name  = models.CharField(max_length=200)
    logo          = models.ImageField(upload_to="sponsors/", blank=True, null=True)
    sponsor_type  = models.CharField(max_length=20, choices=Type.choices)
    amount        = models.DecimalField(max_digits=14, decimal_places=2)
    currency      = models.CharField(max_length=3, default="EUR")
    start_date    = models.DateField()
    end_date      = models.DateField()
    status        = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    contact_name  = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    website       = models.URLField(blank=True)
    contract_file = models.FileField(upload_to="sponsors/contracts/", blank=True, null=True)
    notes         = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("sponsorship")
        verbose_name_plural = _("sponsorships")
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.company_name} ({self.sponsor_type})"


class Investment(models.Model):
    class Type(models.TextChoices):
        EQUITY   = "equity",   _("Equity Investment")
        LOAN     = "loan",     _("Loan")
        GRANT    = "grant",    _("Grant")
        DONATION = "donation", _("Donation")
        OTHER    = "other",    _("Other")

    club          = models.ForeignKey(
        "organizations.Club", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="investments", verbose_name=_("club"),
    )
    investor_name = models.CharField(max_length=200)
    investor_type = models.CharField(max_length=20, choices=Type.choices)
    amount        = models.DecimalField(max_digits=14, decimal_places=2)
    date          = models.DateField()
    equity_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes         = models.TextField(blank=True)
    is_active     = models.BooleanField(default=True)
    contact_email = models.EmailField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("investment")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.investor_name} — €{self.amount}"


# ─── Merchandise E-Commerce ──────────────────────────────────────────────────

class Product(models.Model):
    class Category(models.TextChoices):
        JERSEY      = "jersey",      _("Jersey")
        TRAINING    = "training",    _("Training Gear")
        ACCESSORIES = "accessories", _("Accessories")
        MEMORABILIA = "memorabilia", _("Memorabilia")
        DIGITAL     = "digital",     _("Digital")
        OTHER       = "other",       _("Other")

    name        = models.CharField(max_length=200)
    slug        = models.SlugField(unique=True)
    category    = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    stock       = models.PositiveIntegerField(default=0)
    image       = models.ImageField(upload_to="products/", blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("product")
        ordering = ["category", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("finance:product_detail", kwargs={"slug": self.slug})


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING    = "pending",    _("Pending")
        CONFIRMED  = "confirmed",  _("Confirmed")
        SHIPPED    = "shipped",    _("Shipped")
        DELIVERED  = "delivered",  _("Delivered")
        CANCELLED  = "cancelled",  _("Cancelled")

    customer    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="orders",
    )
    status      = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    total       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_address = models.TextField(blank=True)
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("order")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} — {self.customer}"

    def calculate_total(self):
        from django.db.models import Sum, F, ExpressionWrapper, DecimalField
        total = self.items.aggregate(
            t=Sum(ExpressionWrapper(F("price") * F("quantity"), output_field=DecimalField()))
        )["t"] or 0
        self.total = total
        self.save(update_fields=["total"])
        return total


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product  = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveSmallIntegerField(default=1)
    price    = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot at time of order

    class Meta:
        verbose_name = _("order item")

    def __str__(self):
        return f"{self.quantity}x {self.product} — Order #{self.order_id}"

    @property
    def subtotal(self):
        return self.price * self.quantity


class Cart(models.Model):
    """Session-based or user-based shopping cart."""
    user       = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="cart", null=True, blank=True,
    )
    session_key = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("cart")

    def __str__(self):
        return f"Cart — {self.user or self.session_key}"

    @property
    def total(self):
        from django.db.models import Sum, F, ExpressionWrapper, DecimalField
        return self.cart_items.aggregate(
            t=Sum(ExpressionWrapper(F("price") * F("quantity"), output_field=DecimalField()))
        )["t"] or 0

    @property
    def item_count(self):
        from django.db.models import Sum
        return self.cart_items.aggregate(t=Sum("quantity"))["t"] or 0


class CartItem(models.Model):
    cart     = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)
    price    = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = [("cart", "product")]

    def __str__(self):
        return f"{self.quantity}x {self.product}"

    @property
    def subtotal(self):
        return self.price * self.quantity
