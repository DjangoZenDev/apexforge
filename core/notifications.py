"""
ApexForge email notification helpers.

Usage:
  from core.notifications import send_daily_digest, send_injury_alert, send_contract_expiry_alert
"""
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

SITE_URL = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")


def _send_html(subject, template, context, recipient_list):
    """Render an HTML email template and send it."""
    html_body = render_to_string(template, context)
    # Plain-text fallback: strip tags crudely
    import re
    text_body = re.sub(r"<[^>]+>", "", html_body).strip()

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=True)


# ── Injury alert ─────────────────────────────────────────────────────────────

def send_injury_alert(injury_pk):
    """
    Send an injury alert to all managers of the injured player's club.
    Called from a Django signal after Injury.save().
    """
    from medical.models import Injury
    from organizations.models import UserClubAccess

    try:
        injury = Injury.objects.select_related("player").get(pk=injury_pk)
    except Injury.DoesNotExist:
        return

    # Find managers via the player's team → club
    club = None
    roster = injury.player.rosters.select_related("team__club").filter(is_active=True).first()
    if roster and roster.team.club:
        club = roster.team.club

    if club:
        managers = UserClubAccess.objects.filter(
            club=club, role__in=["owner", "admin", "manager"]
        ).select_related("user")
        recipients = [a.user.email for a in managers if a.user.email]
    else:
        # Fall back: all managers in the system
        from accounts.models import User
        recipients = list(
            User.objects.filter(role__in=["club_owner", "manager"], is_active=True)
            .values_list("email", flat=True)
        )

    if not recipients:
        return

    _send_html(
        subject=f"🏥 Injury Report — {injury.player.full_name}",
        template="emails/injury_alert.html",
        context={"injury": injury, "site_url": SITE_URL},
        recipient_list=recipients,
    )


# ── Contract expiry alert ─────────────────────────────────────────────────────

def send_contract_expiry_alert(contract_pk, days_left):
    """Send a single contract-expiry warning to all managers."""
    from contracts.models import Contract
    from accounts.models import User

    try:
        contract = Contract.objects.get(pk=contract_pk)
    except Contract.DoesNotExist:
        return

    recipients = list(
        User.objects.filter(role__in=["club_owner", "manager"], is_active=True)
        .values_list("email", flat=True)
    )
    if not recipients:
        return

    _send_html(
        subject=f"⚠️ Contract Expiring in {days_left} days — {contract.title}",
        template="emails/contract_expiry.html",
        context={"contract": contract, "days_left": days_left, "site_url": SITE_URL},
        recipient_list=recipients,
    )


# ── Daily digest ──────────────────────────────────────────────────────────────

def send_daily_digest():
    """
    Build and send the daily digest to every manager/owner.
    Called by the Q-cluster schedule (or manually via management command).
    """
    from accounts.models import User
    from contracts.models import Contract
    from medical.models import Injury
    from django.utils import timezone
    import datetime

    today = timezone.now().date()
    in_30 = today + datetime.timedelta(days=30)

    # Expiring contracts (next 30 days)
    expiring = []
    for c in Contract.objects.filter(
        status="active", end_date__lte=in_30, end_date__gte=today
    ):
        delta = (c.end_date - today).days
        c.days_left = delta
        expiring.append(c)
    expiring.sort(key=lambda c: c.days_left)

    # Active injuries
    active_injuries = list(
        Injury.objects.filter(status="active").select_related("player")
    )

    # Overdue tasks
    overdue_tasks = []
    try:
        from staff.models import Task
        overdue_tasks = list(
            Task.objects.filter(
                status__in=["pending", "in_progress"],
                due_date__lt=today,
            ).select_related("assigned_to")
        )
    except Exception:
        pass

    # Send to every manager and owner
    managers = User.objects.filter(
        role__in=["super_admin", "club_owner", "manager"],
        is_active=True,
    ).exclude(email="")

    for user in managers:
        _send_html(
            subject=f"📊 ApexForge Daily Digest — {today}",
            template="emails/daily_digest.html",
            context={
                "user": user,
                "club_name": "ApexForge",
                "today": today,
                "expiring_contracts": expiring,
                "active_injuries": active_injuries,
                "overdue_tasks": overdue_tasks,
                "site_url": SITE_URL,
            },
            recipient_list=[user.email],
        )
