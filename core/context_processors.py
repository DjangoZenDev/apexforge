"""
Global template context — branding, notifications count, active club, cart
"""
from .models import ClubBranding, Notification


def global_context(request):
    ctx = {"branding": ClubBranding.get_solo()}

    if request.user.is_authenticated:
        ctx["unread_count"] = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()

        # Active club (set by ClubContextMiddleware)
        ctx["active_club"] = getattr(request, "active_club", None)

        # All clubs this user can access — for the sidebar switcher
        from organizations.models import UserClubAccess
        ctx["user_clubs"] = list(
            UserClubAccess.objects.select_related("club")
            .filter(user=request.user, club__is_active=True)
            .order_by("-is_primary", "club__name")
            .values_list("club__pk", "club__name", "is_primary")
        )

        # Cart item count for the topnav badge
        try:
            from finance.models import Cart
            cart_obj, _ = Cart.objects.get_or_create(user=request.user)
            ctx["cart"] = cart_obj
        except Exception:
            ctx["cart"] = None
    else:
        ctx["active_club"] = None
        ctx["user_clubs"] = []
        # Guest cart (session-based) — count from session key
        try:
            if request.session.session_key:
                from finance.models import Cart
                cart_obj = Cart.objects.filter(session_key=request.session.session_key).first()
                ctx["cart"] = cart_obj
            else:
                ctx["cart"] = None
        except Exception:
            ctx["cart"] = None

    return ctx
