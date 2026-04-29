"""
Accounts views — login, register, profile, password management
"""
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from .forms import LoginForm, RegisterForm, UserProfileForm, CustomPasswordResetForm, CustomSetPasswordForm
from .models import User


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_fan_investor:
            return redirect("fans:portal")
        return redirect("core:dashboard")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        remember = form.cleaned_data.get("remember_me")
        if not remember:
            request.session.set_expiry(0)
        login(request, user)
        messages.success(request, _("Welcome back, %(name)s!") % {"name": user.get_short_name() or user.email})
        next_url = request.GET.get("next")
        if next_url:
            return redirect(next_url)
        # Route based on role: fans go to fan portal, staff go to dashboard
        if user.is_fan_investor:
            return redirect("fans:portal")
        return redirect("core:dashboard")

    return render(request, "accounts/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_fan_investor:
            return redirect("fans:portal")
        return redirect("core:dashboard")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, _("Account created! Welcome to ApexForge."))
        if user.is_fan_investor:
            return redirect("fans:portal")
        return redirect("core:dashboard")

    return render(request, "accounts/register.html", {"form": form})


@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    messages.info(request, _("You have been signed out."))
    next_url = request.POST.get("next", "")
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("core:landing")


@login_required
def profile_view(request):
    profile = request.user.profile
    form = UserProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=profile,
        initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        },
    )
    if request.method == "POST" and form.is_valid():
        request.user.first_name = form.cleaned_data["first_name"]
        request.user.last_name  = form.cleaned_data["last_name"]
        request.user.save(update_fields=["first_name", "last_name"])
        form.save()
        messages.success(request, _("Profile updated successfully."))
        if request.htmx:
            from django.template.loader import render_to_string
            html = render_to_string("partials/toast.html", {"message": str(_("Profile updated successfully.")), "tag": "success"}, request)
            from django.http import HttpResponse
            response = HttpResponse(html)
            response["HX-Trigger"] = "showToast"
            return response
        return redirect("accounts:profile")

    return render(request, "accounts/profile.html", {"form": form, "profile": profile})


class ApexPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "accounts/password_reset.html"
    email_template_name = "registration/password_reset_email.html"
    success_url = "/accounts/password-reset/done/"


class ApexPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = "accounts/password_reset_confirm.html"
    success_url = "/accounts/password-reset/complete/"
