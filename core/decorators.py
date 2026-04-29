"""
Role-based access decorators for ApexForge.
"""
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _


def staff_required(view_func):
    """
    Allow only staff roles (Super Admin, Club Owner, Manager, Coach, Scout, Athlete).
    Fan / Investor accounts are redirected to the fan portal.
    Unauthenticated users go to the login page.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if request.user.is_fan_investor:
            messages.warning(
                request,
                _("This area is for club staff only. You have been redirected to your fan portal."),
            )
            return redirect("fans:portal")
        return view_func(request, *args, **kwargs)
    return wrapper


def manager_required(view_func):
    """
    Allow only managing roles (Super Admin, Club Owner, Manager).
    Coaches, scouts, athletes, and fans are redirected to the dashboard.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not request.user.can_manage:
            messages.warning(request, _("You do not have permission to access this page."))
            if request.user.is_fan_investor:
                return redirect("fans:portal")
            return redirect("core:dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper
