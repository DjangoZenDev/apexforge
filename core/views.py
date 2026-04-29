"""
Core views — dashboard, search, notifications, activity log
"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.utils.translation import gettext_lazy as _

from .models import ActivityLog, Notification, ClubBranding


def landing(request):
    """Public marketing homepage — visible to all visitors including logged-in users."""
    from marketing.models import NewsPost, Announcement
    from finance.models import Product
    from fans.models import Ticket, TicketCategory
    from events.models import Event
    from videos.models import Video
    from django.utils import timezone

    branding = ClubBranding.get_solo()

    # Latest published news
    news_qs = NewsPost.objects.filter(is_published=True).select_related("author").order_by("-published_at")
    featured_news = news_qs.filter(is_featured=True).first()
    latest_news = news_qs[:6]

    # Public videos
    videos = (
        Video.objects.filter(is_public=True)
        .order_by("-created_at")[:4]
    )

    # Featured shop products
    featured_products = (
        Product.objects.filter(is_active=True)
        .order_by("?")[:8]
    )

    # Upcoming events with available tickets
    upcoming_events = (
        Event.objects.filter(
            status="scheduled",
            start_date__gte=timezone.now().date(),
            tickets__status=Ticket.Status.AVAILABLE,
        )
        .distinct()
        .prefetch_related("tickets__category")
        .order_by("start_date")[:4]
    )

    # Active announcement banner
    announcement = (
        Announcement.objects.filter(is_active=True)
        .order_by("-created_at")
        .first()
    )

    return render(request, "landing.html", {
        "branding": branding,
        "latest_news": latest_news,
        "featured_news": featured_news,
        "videos": videos,
        "featured_products": featured_products,
        "upcoming_events": upcoming_events,
        "announcement": announcement,
    })


@login_required
def dashboard(request):
    """Role-aware landing dashboard with KPIs."""
    from teams.models import Team
    from players.models import Player
    from events.models import Event
    from finance.models import Transaction
    from django.utils import timezone
    import datetime

    from django.db.models import Sum

    user = request.user
    club = getattr(request, "active_club", None)
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # KPIs (scoped to active club when available)
    kpis = {}

    if user.can_manage or user.is_super_admin:
        team_qs  = Team.objects.filter(club=club) if club else Team.objects.all()
        event_qs = Event.objects.filter(team__club=club) if club else Event.objects.all()
        kpis["total_teams"]   = team_qs.count()
        kpis["total_players"] = (
            Player.objects.filter(rosters__team__club=club).distinct().count()
            if club else Player.objects.count()
        )
        kpis["upcoming_events"] = event_qs.filter(
            start_date__gte=today, status=Event.Status.SCHEDULED
        ).count()
        kpis["monthly_income"] = Transaction.objects.filter(
            transaction_type=Transaction.Type.INCOME,
            date__gte=month_start,
        ).aggregate(total=Sum("amount"))["total"] or 0
        kpis["monthly_expense"] = Transaction.objects.filter(
            transaction_type=Transaction.Type.EXPENSE,
            date__gte=month_start,
        ).aggregate(total=Sum("amount"))["total"] or 0

    upcoming_qs = Event.objects.filter(
        start_date__gte=today, status=Event.Status.SCHEDULED
    )
    if club:
        upcoming_qs = upcoming_qs.filter(team__club=club)
    upcoming_events = upcoming_qs.select_related("team").order_by("start_date")[:5]

    recent_activity = ActivityLog.objects.select_related("user").order_by("-created_at")[:10]

    notifications = Notification.objects.filter(
        recipient=user, is_read=False
    ).order_by("-created_at")[:5]

    # Chart data (last 6 months income vs expense)
    chart_labels, chart_income, chart_expense = _get_monthly_chart_data()

    context = {
        "kpis": kpis,
        "upcoming_events": upcoming_events,
        "recent_activity": recent_activity,
        "notifications": notifications,
        "chart_labels":  chart_labels,
        "chart_income":  chart_income,
        "chart_expense": chart_expense,
    }
    return render(request, "core/dashboard.html", context)


def _get_monthly_chart_data():
    from finance.models import Transaction
    from django.utils import timezone
    from django.db.models import Sum
    from django.db.models.functions import TruncMonth
    import datetime

    today = timezone.now().date()
    six_months_ago = today - datetime.timedelta(days=180)

    qs = (
        Transaction.objects
        .filter(date__gte=six_months_ago)
        .annotate(month=TruncMonth("date"))
        .values("month", "transaction_type")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    months = {}
    for row in qs:
        key = row["month"].strftime("%b %Y")
        if key not in months:
            months[key] = {"income": 0, "expense": 0}
        if row["transaction_type"] == Transaction.Type.INCOME:
            months[key]["income"] = float(row["total"])
        else:
            months[key]["expense"] = float(row["total"])

    labels  = list(months.keys())
    income  = [months[k]["income"]  for k in labels]
    expense = [months[k]["expense"] for k in labels]
    return labels, income, expense


@login_required
@require_GET
def search(request):
    query = request.GET.get("q", "").strip()
    results = []
    if len(query) >= 2:
        from teams.models import Team
        from players.models import Player
        from events.models import Event
        from marketing.models import NewsPost

        for team in Team.objects.filter(name__icontains=query)[:5]:
            results.append({"type": "Team", "label": team.name, "url": team.get_absolute_url()})
        for player in Player.objects.filter(
            full_name__icontains=query
        ).select_related("user")[:5]:
            results.append({"type": "Player", "label": player.full_name, "url": player.get_absolute_url()})
        for event in Event.objects.filter(title__icontains=query)[:5]:
            results.append({"type": "Event", "label": event.title, "url": event.get_absolute_url()})
        for post in NewsPost.objects.filter(title__icontains=query, is_published=True)[:3]:
            results.append({"type": "News", "label": post.title, "url": post.get_absolute_url()})

    if request.htmx:
        return render(request, "partials/search_results.html", {"results": results, "query": query})
    return JsonResponse({"results": results})


@login_required
def notifications_panel(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by("-created_at")[:20]
    return render(request, "partials/notifications.html", {"notifications": notifications})


@login_required
@require_POST
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save(update_fields=["is_read"])
    return render(request, "partials/notification_item.html", {"notification": notif})


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    if request.htmx:
        from django.http import HttpResponse
        return HttpResponse('<span class="text-emerald-600 text-sm">All marked as read</span>')
    return JsonResponse({"status": "ok"})


@login_required
def activity_log(request):
    logs = ActivityLog.objects.select_related("user").order_by("-created_at")[:100]
    return render(request, "core/activity_log.html", {"logs": logs})


@login_required
def branding_settings(request):
    if not request.user.can_manage:
        from django.contrib import messages
        messages.error(request, _("You do not have permission to access branding settings."))
        return __import__("django.shortcuts", fromlist=["redirect"]).redirect("core:dashboard")

    from .forms import ClubBrandingForm
    branding = ClubBranding.get_solo()
    form = ClubBrandingForm(request.POST or None, request.FILES or None, instance=branding)
    if request.method == "POST" and form.is_valid():
        form.save()
        from django.contrib import messages
        messages.success(request, _("Branding settings updated."))
        from django.shortcuts import redirect
        return redirect("core:branding")
    return render(request, "core/branding.html", {"form": form, "branding": branding})


@login_required
def upgrade(request):
    """Free edition — shown when a Pro-only feature is accessed."""
    features = [
        "Events & Calendar", "Scouting & Recruitment",
        "Finance & Commerce", "Medical Records",
        "Contract Management", "Staff Management",
        "Tournaments", "Academy & Youth",
        "Inventory", "Marketing & News",
        "Analytics & Insights", "Video Management",
        "Fan Portal & Ticketing", "Organization Management",
        "PDF & Excel Export",
    ]
    return render(request, "core/upgrade.html", {"features": features})


def public_faq(request):
    """Publicly accessible FAQ page."""
    from .models import ClubBranding
    branding = ClubBranding.get_solo()
    faq_sections = [
        {
            "icon": "🏠",
            "title": _("About the Platform"),
            "items": [
                {"q": _("What is ApexForge?"),
                 "a": _("ApexForge is a complete sports management and fan engagement platform. It covers player management, ticketing, an online club store, loyalty points, media, and much more.")},
                {"q": _("Who can use ApexForge?"),
                 "a": _("ApexForge is designed for sports clubs, players, staff, fans, and investors. Different roles have access to different features.")},
                {"q": _("Is registration free?"),
                 "a": _("Creating a fan account is free. Club and staff accounts are managed by club administrators. Contact us if you'd like to onboard your club.")},
            ],
        },
        {
            "icon": "🎟️",
            "title": _("Tickets & Events"),
            "items": [
                {"q": _("How do I buy a ticket?"),
                 "a": _("Sign in to your account, go to Tickets in the sidebar or click 'Get Tickets' on your fan portal, select an event and category, then complete payment via Stripe.")},
                {"q": _("Where do I find my tickets after purchase?"),
                 "a": _("Go to 'My Tickets' in the sidebar. All purchased tickets with reference codes are listed there.")},
                {"q": _("Are tickets refundable?"),
                 "a": _("Tickets are generally non-refundable unless the event is cancelled or rescheduled. Contact support if you have a special circumstance.")},
                {"q": _("Do I earn loyalty points when buying tickets?"),
                 "a": _("Yes! You earn 1 loyalty point for every €1 spent on tickets. Points are added automatically after payment is confirmed.")},
            ],
        },
        {
            "icon": "🛍️",
            "title": _("Club Store & Orders"),
            "items": [
                {"q": _("How do I browse the club store?"),
                 "a": _("Click 'Club Store' in the sidebar or 'Shop Now' on your fan portal. You can filter by category and browse all available items.")},
                {"q": _("What payment methods are accepted?"),
                 "a": _("We accept Visa, Mastercard, iDEAL, and Bancontact via Stripe. PayPal is not currently supported.")},
                {"q": _("How do I track my order?"),
                 "a": _("Go to 'My Orders' in the sidebar. You'll see the current status of every order (Confirmed, Shipped, Delivered).")},
                {"q": _("Can I return a product?"),
                 "a": _("Yes. Return unused items in original packaging within 14 days. Email support to start a return.")},
            ],
        },
        {
            "icon": "⭐",
            "title": _("Loyalty Points & Membership"),
            "items": [
                {"q": _("How do loyalty points work?"),
                 "a": _("You earn 1 point for every €1 spent on tickets or shop orders. Points accumulate and unlock higher membership tiers (Bronze → Silver → Gold → Platinum).")},
                {"q": _("What are the membership tiers?"),
                 "a": _("Bronze (0 pts), Silver (500 pts), Gold (2,000 pts), Platinum (5,000 pts). Higher tiers unlock exclusive perks, discounts, and priority access.")},
                {"q": _("Where can I see my loyalty points balance?"),
                 "a": _("Your points are displayed on your Fan Portal and in 'Loyalty Points' in the sidebar.")},
            ],
        },
        {
            "icon": "👤",
            "title": _("Account & Profile"),
            "items": [
                {"q": _("How do I change my password?"),
                 "a": _("Go to Account Profile (click your avatar in the top-right corner) and use the 'Change Password' section, or use 'Forgot Password' on the login page.")},
                {"q": _("How do I update my fan profile photo?"),
                 "a": _("Your fan portal photo and your account photo are separate. The fan portal photo is set under 'Fan Profile' in the sidebar. Your account avatar is set in Account Profile (top-right avatar).")},
                {"q": _("How do I delete my account?"),
                 "a": _("Email us at support@apexforge.com to request account deletion. All personal data will be removed within 30 days in compliance with GDPR.")},
            ],
        },
        {
            "icon": "💳",
            "title": _("Payments & Security"),
            "items": [
                {"q": _("Is my payment information safe?"),
                 "a": _("Yes. We never store your card details. All payments are handled by Stripe, a PCI-DSS Level 1 certified provider.")},
                {"q": _("I was charged but didn't receive a confirmation. What do I do?"),
                 "a": _("Check 'My Orders' or 'My Tickets'. If the order shows Pending after 10 minutes, email support with your payment reference number.")},
                {"q": _("What currencies are accepted?"),
                 "a": _("All prices are in Euros (€). Your bank may charge a conversion fee if your card is in a different currency.")},
            ],
        },
    ]
    return render(request, "core/public_faq.html", {
        "branding": branding,
        "faq_sections": faq_sections,
    })


def terms(request):
    """Terms of Service page."""
    from .models import ClubBranding
    branding = ClubBranding.get_solo()
    return render(request, "core/terms.html", {"branding": branding})


def privacy_policy(request):
    """Privacy Policy page."""
    from .models import ClubBranding
    branding = ClubBranding.get_solo()
    return render(request, "core/privacy.html", {"branding": branding})


def contact(request):
    """Public contact form — saves to DB and optionally emails."""
    from .models import ClubBranding, ContactMessage
    branding = ClubBranding.get_solo()
    form_sent = False
    form_data = {}

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name  = request.POST.get("last_name", "").strip()
        email      = request.POST.get("email", "").strip()
        subject    = request.POST.get("subject", "general")
        message    = request.POST.get("message", "").strip()
        agree      = request.POST.get("agree")

        errors = []
        if not first_name: errors.append(_("First name is required."))
        if not last_name:  errors.append(_("Last name is required."))
        if not email:      errors.append(_("Email address is required."))
        if not message:    errors.append(_("Message is required."))
        if not agree:      errors.append(_("You must agree to the Privacy Policy."))

        if not errors:
            ContactMessage.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                subject=subject,
                message=message,
                ip_address=request.META.get("REMOTE_ADDR"),
            )
            form_sent = True
        else:
            from django.contrib import messages as dj_messages
            for e in errors:
                dj_messages.error(request, e)
            form_data = request.POST
    else:
        # Pre-fill for logged-in users
        if request.user.is_authenticated:
            form_data = {
                "first_name": request.user.first_name,
                "last_name":  request.user.last_name,
                "email":      request.user.email,
            }

    return render(request, "core/contact.html", {
        "branding":  branding,
        "form_sent": form_sent,
        "form":      form_data,
    })


@login_required
def help_center(request):
    from django.utils.translation import gettext as _t
    help_nav = [
        ("dashboard",     _t("Dashboard")),
        ("players",       _t("Players")),
        ("teams",         _t("Teams")),
        ("events",        _t("Events")),
        ("tournaments",   _t("Tournaments")),
        ("contracts",     _t("Contracts")),
        ("staff",         _t("Staff")),
        ("medical",       _t("Medical")),
        ("finance",       _t("Finance")),
        ("inventory",     _t("Inventory")),
        ("scouting",      _t("Scouting")),
        ("organizations", _t("Organizations")),
        ("academy",       _t("Academy")),
        ("marketing",     _t("Marketing")),
        ("videos",        _t("Videos")),
        ("fans",          _t("Fans")),
        ("insights",      _t("Insights")),
    ]
    return render(request, "core/help.html", {"help_nav": help_nav})

