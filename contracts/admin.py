from django.contrib import admin
from .models import Contract, ContractClause


class ClauseInline(admin.TabularInline):
    model = ContractClause
    extra = 0


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ["title", "contract_type", "party_name", "status", "start_date", "end_date", "value"]
    list_filter = ["contract_type", "status", "currency"]
    search_fields = ["title", "party_name"]
    inlines = [ClauseInline]
