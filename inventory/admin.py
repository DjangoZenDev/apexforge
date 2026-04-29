from django.contrib import admin
from .models import ItemCategory, InventoryItem, StockMovement, KitAssignment


@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "icon"]


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ["name", "sku", "category", "quantity", "min_quantity", "unit_price", "is_low_stock"]
    list_filter = ["category", "is_active", "team"]
    search_fields = ["name", "sku"]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ["item", "movement_type", "quantity", "date", "performed_by"]
    list_filter = ["movement_type"]


@admin.register(KitAssignment)
class KitAssignmentAdmin(admin.ModelAdmin):
    list_display = ["item", "assigned_to_player", "quantity", "assigned_date", "is_returned"]
    list_filter = ["is_returned"]
