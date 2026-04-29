"""
Core middleware — activity logging + active-club context
"""
from django.utils.deprecation import MiddlewareMixin


class ClubContextMiddleware(MiddlewareMixin):
    """
    Attach request.active_club on every authenticated request.

    Priority:
      1. session["active_club_id"]  – user explicitly switched clubs
      2. User's primary club        – is_primary=True on UserClubAccess
      3. First accessible club      – earliest granted_at
      4. None                       – super-admin with no club access or anonymous
    """

    _SKIP_PREFIXES = ("/static/", "/media/", "/admin/", "/favicon")

    def process_request(self, request):
        path = request.path_info
        if any(path.startswith(p) for p in self._SKIP_PREFIXES):
            request.active_club = None
            return

        if not request.user.is_authenticated:
            request.active_club = None
            return

        from organizations.models import UserClubAccess

        club_id = request.session.get("active_club_id")
        active_club = None

        if club_id:
            try:
                access = UserClubAccess.objects.select_related("club").get(
                    user=request.user, club_id=club_id, club__is_active=True
                )
                active_club = access.club
            except UserClubAccess.DoesNotExist:
                request.session.pop("active_club_id", None)
                request.session.pop("active_club_name", None)

        if active_club is None:
            access = (
                UserClubAccess.objects.select_related("club")
                .filter(user=request.user, club__is_active=True)
                .order_by("-is_primary", "granted_at")
                .first()
            )
            if access:
                active_club = access.club
                request.session["active_club_id"] = access.club.pk
                request.session["active_club_name"] = access.club.name

        request.active_club = active_club


class ActivityLogMiddleware(MiddlewareMixin):
    """Light middleware; actual logging done in views via ActivityLog.log()."""

    SKIP_PATHS = ("/static/", "/media/", "/admin/jsi18n/", "/favicon")

    def process_request(self, request):
        request._client_ip = self._get_client_ip(request)

    @staticmethod
    def _get_client_ip(request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class FreeVersionMiddleware:
    """Redirects Pro-only URL namespaces to the upgrade page."""
    SKIP_PREFIXES = ("/static/", "/media/", "/admin/", "/accounts/", "/favicon")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.conf import settings
        path = request.path_info
        if any(path.startswith(p) for p in self.SKIP_PREFIXES):
            return self.get_response(request)
        if request.user.is_authenticated:
            match = getattr(request, "resolver_match", None)
            locked = getattr(settings, "FREE_EDITION_LOCKED_NAMESPACES", frozenset())
            if match and match.namespace in locked:
                from django.shortcuts import redirect
                from django.urls import reverse
                return redirect(reverse("core:upgrade"))
        return self.get_response(request)
