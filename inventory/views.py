"""Inventory views — items, stock movements, kit assignments"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _

from .models import InventoryItem, ItemCategory, StockMovement, KitAssignment
from .forms import InventoryItemForm, StockMovementForm, KitAssignmentForm


@login_required
def inventory_list(request):
    qs = InventoryItem.objects.select_related("category", "team").filter(is_active=True)
    category = request.GET.get("category")
    q = request.GET.get("q", "")
    low_stock = request.GET.get("low_stock")
    if category:
        qs = qs.filter(category_id=category)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q))
    if low_stock:
        qs = [i for i in qs if i.is_low_stock]
    else:
        qs = list(qs)

    total_value = sum(i.total_value for i in qs)
    low_stock_count = InventoryItem.objects.filter(is_active=True).count()

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page", 1))
    categories = ItemCategory.objects.all()
    return render(request, "inventory/list.html", {
        "page": page,
        "categories": categories,
        "total_value": total_value,
        "low_stock_count": sum(1 for i in qs if i.is_low_stock),
    })


@login_required
def item_detail(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    movements = item.movements.order_by("-created_at")[:20]
    assignments = item.assignments.filter(is_returned=False).select_related(
        "assigned_to_player", "assigned_to_user")
    return render(request, "inventory/item_detail.html", {
        "item": item, "movements": movements, "assignments": assignments,
    })


@login_required
def item_create(request):
    form = InventoryItemForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Item added to inventory."))
        return redirect("inventory:list")
    return render(request, "inventory/item_form.html", {"form": form, "title": _("Add Item")})


@login_required
def item_edit(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    form = InventoryItemForm(request.POST or None, request.FILES or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Item updated."))
        return redirect("inventory:item_detail", pk=pk)
    return render(request, "inventory/item_form.html", {"form": form, "title": _("Edit Item"), "item": item})


@login_required
def stock_movement(request, item_pk):
    item = get_object_or_404(InventoryItem, pk=item_pk)
    form = StockMovementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        mv = form.save(commit=False)
        mv.item = item
        mv.performed_by = request.user
        # Adjust quantity sign based on movement type
        if mv.movement_type == StockMovement.MovementType.OUT:
            mv.quantity = -abs(mv.quantity)
        else:
            mv.quantity = abs(mv.quantity)
        mv.save()
        messages.success(request, _("Stock updated."))
        return redirect("inventory:item_detail", pk=item_pk)
    return render(request, "inventory/movement_form.html", {"form": form, "item": item})


@login_required
def kit_assign(request, item_pk):
    item = get_object_or_404(InventoryItem, pk=item_pk)
    form = KitAssignmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        assignment = form.save(commit=False)
        assignment.item = item
        assignment.save()
        messages.success(request, _("Kit assigned."))
        return redirect("inventory:item_detail", pk=item_pk)
    return render(request, "inventory/assign_form.html", {"form": form, "item": item})


@login_required
def kit_return(request, pk):
    assignment = get_object_or_404(KitAssignment, pk=pk)
    from django.utils import timezone
    assignment.is_returned = True
    assignment.actual_return = timezone.now().date()
    assignment.save(update_fields=["is_returned", "actual_return"])
    messages.success(request, _("Kit marked as returned."))
    return redirect("inventory:item_detail", pk=assignment.item.pk)
