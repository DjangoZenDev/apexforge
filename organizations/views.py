"""Multi-Club Organizations views"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _

from .models import Organization, Club, UserClubAccess
from .forms import OrganizationForm, ClubForm, ClubAccessForm


# ─── Organizations ────────────────────────────────────────────────────────────

@login_required
def org_list(request):
    orgs = Organization.objects.prefetch_related("clubs").filter(is_active=True)
    return render(request, "organizations/list.html", {"orgs": orgs})


@login_required
def org_detail(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    clubs = org.clubs.prefetch_related("user_accesses").filter(is_active=True)
    return render(request, "organizations/detail.html", {"org": org, "clubs": clubs})


@login_required
def org_create(request):
    form = OrganizationForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Organization created."))
        return redirect("organizations:list")
    return render(request, "organizations/org_form.html", {
        "form": form, "title": _("New Organization"),
    })


@login_required
def org_edit(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    form = OrganizationForm(request.POST or None, request.FILES or None, instance=org)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Organization updated."))
        return redirect("organizations:detail", pk=pk)
    return render(request, "organizations/org_form.html", {
        "form": form, "title": _("Edit Organization"), "org": org,
    })


# ─── Clubs ────────────────────────────────────────────────────────────────────

@login_required
def club_detail(request, pk):
    club = get_object_or_404(Club.objects.select_related("organization"), pk=pk)
    accesses = club.user_accesses.select_related("user").order_by("role")
    return render(request, "organizations/club_detail.html", {
        "club": club, "accesses": accesses,
    })


@login_required
def club_create(request, org_pk):
    org = get_object_or_404(Organization, pk=org_pk)
    form = ClubForm(request.POST or None, request.FILES or None,
                    initial={"organization": org})
    if request.method == "POST" and form.is_valid():
        club = form.save()
        messages.success(request, _("Club created."))
        return redirect("organizations:club_detail", pk=club.pk)
    return render(request, "organizations/club_form.html", {
        "form": form, "org": org, "title": _("New Club"),
    })


@login_required
def club_edit(request, pk):
    club = get_object_or_404(Club, pk=pk)
    form = ClubForm(request.POST or None, request.FILES or None, instance=club)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Club updated."))
        return redirect("organizations:club_detail", pk=pk)
    return render(request, "organizations/club_form.html", {
        "form": form, "org": club.organization, "title": _("Edit Club"),
    })


# ─── User access management ───────────────────────────────────────────────────

@login_required
def manage_access(request, club_pk):
    club = get_object_or_404(Club, pk=club_pk)
    form = ClubAccessForm(request.POST or None, initial={"club": club})
    if request.method == "POST" and form.is_valid():
        access = form.save(commit=False)
        access.club = club
        access.granted_by = request.user
        access.save()
        messages.success(request, _("Access granted."))
        return redirect("organizations:club_detail", pk=club_pk)
    accesses = club.user_accesses.select_related("user")
    return render(request, "organizations/access_form.html", {
        "form": form, "club": club, "accesses": accesses,
    })


@login_required
def revoke_access(request, access_pk):
    access = get_object_or_404(UserClubAccess, pk=access_pk)
    club_pk = access.club.pk
    access.delete()
    messages.success(request, _("Access revoked."))
    return redirect("organizations:club_detail", pk=club_pk)


# ─── Club switcher ───────────────────────────────────────────────────────────

@login_required
def switch_club(request, club_pk):
    """Store active club in session for context switching."""
    club = get_object_or_404(Club, pk=club_pk)
    # Only allow switching if the user has access
    has_access = UserClubAccess.objects.filter(user=request.user, club=club).exists()
    if has_access or request.user.is_staff:
        request.session["active_club_id"] = club_pk
        request.session["active_club_name"] = club.name
        messages.success(request, _("Switched to %(club)s.") % {"club": club.name})
    else:
        messages.error(request, _("You don't have access to that club."))
    return redirect(request.META.get("HTTP_REFERER", "organizations:list"))
