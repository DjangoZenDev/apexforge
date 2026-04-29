from django.contrib import admin
from .models import (
    BudgetCategory, Budget, Transaction, Sponsorship, Investment,
    Product, Order, OrderItem, Cart, CartItem,
)


@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "color")


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("name", "amount", "season", "team", "category")
    list_filter  = ("season", "team")


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    fields = ("title", "transaction_type", "amount", "date", "status")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display  = ("title", "transaction_type", "amount", "date", "status", "category")
    list_filter   = ("transaction_type", "status", "category")
    search_fields = ("title", "reference")
    date_hierarchy = "date"


@admin.register(Sponsorship)
class SponsorshipAdmin(admin.ModelAdmin):
    list_display = ("company_name", "sponsor_type", "amount", "status", "start_date", "end_date")
    list_filter  = ("sponsor_type", "status")


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ("investor_name", "investor_type", "amount", "date", "is_active")
    list_filter  = ("investor_type", "is_active")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ("name", "category", "price", "stock", "is_active")
    list_filter   = ("category", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("pk", "customer", "total", "status", "created_at")
    list_filter  = ("status",)
    inlines      = [OrderItemInline]
