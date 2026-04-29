"""Contracts views"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Contract, ContractClause
from .forms import ContractForm, ContractClauseForm
from core.pdf import contract_pdf


@login_required
def contract_list(request):
    qs = Contract.objects.select_related("player", "team", "created_by").order_by("-created_at")
    contract_type = request.GET.get("type")
    status = request.GET.get("status")
    q = request.GET.get("q", "")
    if contract_type:
        qs = qs.filter(contract_type=contract_type)
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(party_name__icontains=q))

    # Auto-update expired contracts
    today = timezone.now().date()
    qs.filter(status=Contract.Status.ACTIVE, end_date__lt=today).update(status=Contract.Status.EXPIRED)

    expiring_soon = qs.filter(status=Contract.Status.ACTIVE, end_date__lte=today.replace(day=today.day + 30)
                               if today.day <= 1 else today).count()

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page", 1))
    return render(request, "contracts/list.html", {
        "page": page,
        "type_choices": Contract.ContractType.choices,
        "status_choices": Contract.Status.choices,
    })


@login_required
def contract_detail(request, pk):
    contract = get_object_or_404(Contract.objects.select_related("player", "team", "signed_by", "created_by"), pk=pk)
    clauses = contract.clauses.order_by("order")
    return render(request, "contracts/detail.html", {"contract": contract, "clauses": clauses})


@login_required
def contract_create(request):
    form = ContractForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        contract = form.save(commit=False)
        contract.created_by = request.user
        contract.save()
        messages.success(request, _("Contract created."))
        return redirect("contracts:detail", pk=contract.pk)
    return render(request, "contracts/form.html", {"form": form, "title": _("New Contract")})


@login_required
def contract_edit(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    form = ContractForm(request.POST or None, request.FILES or None, instance=contract)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Contract updated."))
        return redirect("contracts:detail", pk=pk)
    return render(request, "contracts/form.html", {
        "form": form, "title": _("Edit Contract"), "contract": contract,
    })


@login_required
def clause_add(request, contract_pk):
    contract = get_object_or_404(Contract, pk=contract_pk)
    form = ContractClauseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        clause = form.save(commit=False)
        clause.contract = contract
        clause.save()
        messages.success(request, _("Clause added."))
        return redirect("contracts:detail", pk=contract_pk)
    return render(request, "contracts/clause_form.html", {"form": form, "contract": contract})


@login_required
def sign_contract(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if request.method == "POST":
        contract.status = Contract.Status.ACTIVE
        contract.signed_by = request.user
        contract.signed_date = timezone.now().date()
        contract.save(update_fields=["status", "signed_by", "signed_date"])
        messages.success(request, _("Contract marked as signed and active."))
    return redirect("contracts:detail", pk=pk)


@login_required
def contract_pdf_view(request, pk):
    c = get_object_or_404(Contract, pk=pk)
    return contract_pdf(c)
