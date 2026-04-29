from django.contrib import admin
from .models import FanProfile, TicketCategory, Ticket, TicketPurchase, LoyaltyTransaction


@admin.register(FanProfile)
class FanProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "tier", "loyalty_points", "created_at"]
    list_filter  = ["tier"]
    search_fields = ["user__first_name", "user__last_name", "user__email"]


@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "base_price", "color", "is_active"]
    list_filter  = ["is_active"]


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    fields = ["category", "seat_row", "seat_number", "price", "status"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display  = ["event", "category", "seat_row", "seat_number", "status", "owner"]
    list_filter   = ["status", "category"]
    search_fields = ["event__title", "owner__user__first_name"]


@admin.register(TicketPurchase)
class TicketPurchaseAdmin(admin.ModelAdmin):
    list_display = ["reference", "fan", "total_amount", "payment_status", "loyalty_earned", "purchased_at"]
    list_filter  = ["payment_status"]


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ["fan", "points", "tx_type", "description", "created_at"]
    list_filter  = ["tx_type"]
