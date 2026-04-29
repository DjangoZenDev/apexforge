"""Fans & Ticketing views"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.decorators import manager_required
from events.models import Event
from .models import FanProfile, TicketCategory, Ticket, TicketPurchase, LoyaltyTransaction, MembershipTier
from .forms import (
    FanProfileForm, TicketCategoryForm, TicketForm,
    TicketBulkCreateForm, LoyaltyAdjustForm,
)


# ─── Fan portal ──────────────────────────────────────────────────────────────

@login_required
def fan_portal(request):
    """Fan's personal dashboard — profile, tickets, loyalty, shop highlights."""
    from finance.models import Product, Order
    try:
        profile = request.user.fan_profile
    except FanProfile.DoesNotExist:
        profile = None
    upcoming_events = Event.objects.filter(
        status="scheduled", start_date__gte=timezone.now().date()
    ).order_by("start_date")[:4]
    featured_products = Product.objects.filter(is_active=True).order_by("?")[:4]
    my_tickets = []
    my_orders = []
    if profile:
        my_tickets = profile.tickets.select_related("event", "category").order_by("-purchased_at")[:3]
    if request.user.is_authenticated:
        my_orders = Order.objects.filter(customer=request.user).order_by("-created_at")[:3]
    return render(request, "fans/portal.html", {
        "profile": profile,
        "upcoming_events": upcoming_events,
        "featured_products": featured_products,
        "my_tickets": my_tickets,
        "my_orders": my_orders,
    })


@login_required
def fan_help(request):
    ctx = {
        "shopping_faqs": [
            {"q": "How do I browse products?",
             "a": "Go to Club Store in the left sidebar or click Shop Now on your portal. Browse by category using the filter buttons at the top."},
            {"q": "Are product photos accurate?",
             "a": "Yes — all photos show the actual item. Colours may vary slightly depending on your screen settings."},
            {"q": "Is there a size guide?",
             "a": "Size information is listed on each product page. If you're unsure, contact support and we'll help you choose."},
            {"q": "Can I buy the same product multiple times?",
             "a": "Yes. Simply adjust the quantity on the product page before adding to cart, or add the product again and the quantity will update automatically."},
        ],
        "cart_faqs": [
            {"q": "How do I add items to my cart?",
             "a": "Open any product, choose your quantity and click Add to Cart. The cart icon in the top-right updates immediately."},
            {"q": "How do I remove an item from my cart?",
             "a": "Go to My Cart and click the remove (×) button next to the item you want to delete."},
            {"q": "Does my cart save if I log out?",
             "a": "Yes — your cart is saved to your account. Items remain in your cart when you log back in."},
            {"q": "Is there a limit on how many items I can add?",
             "a": "Each item is limited to the available stock shown on the product page."},
        ],
        "payment_faqs": [
            {"q": "How do I pay?",
             "a": "At checkout you are redirected to Stripe's secure payment page where you enter your card details. We accept Visa, Mastercard, iDEAL and Bancontact."},
            {"q": "Is my card information safe?",
             "a": "Completely. We never see or store your card number. All payments are processed by Stripe, a PCI-DSS Level 1 certified payment provider."},
            {"q": "What currencies are accepted?",
             "a": "All prices are in Euros (€). Your bank may charge a conversion fee if your card is in a different currency."},
            {"q": "I was charged but didn't get an order confirmation — what do I do?",
             "a": "Check My Orders in the sidebar. If the order shows Confirmed you're all set. If it shows Pending after 10 minutes, email support@apexforge.com with your payment reference."},
            {"q": "Can I pay with PayPal?",
             "a": "Not at the moment. We accept card payments via Stripe. PayPal support may be added in a future update."},
        ],
        "refund_faqs": [
            {"q": "Can I return a product?",
             "a": "Yes. You may return unused items in original packaging within 14 days of receiving your order. Contact support@apexforge.com to start a return."},
            {"q": "How long does a refund take?",
             "a": "Once your return is received and approved, refunds are processed within 5–10 business days back to your original payment method."},
            {"q": "What if my item arrived damaged or incorrect?",
             "a": "We're sorry to hear that! Email support@apexforge.com with a photo of the item and your order number. We will send a replacement or issue a full refund."},
            {"q": "Can I cancel an order after placing it?",
             "a": "If your order hasn't shipped yet, contact support immediately at support@apexforge.com and we will do our best to cancel it."},
        ],
        "ticket_faqs": [
            {"q": "How do I buy a ticket?",
             "a": "Click Buy Tickets in the sidebar or Get Tickets on your portal. Select an event, choose your ticket category and complete payment via Stripe."},
            {"q": "Where do I find my tickets after purchase?",
             "a": "Go to My Tickets in the sidebar. All purchased tickets with their reference codes are listed there."},
            {"q": "Are ticket purchases refundable?",
             "a": "Tickets are generally non-refundable unless the event is cancelled or rescheduled. Contact support@apexforge.com if you have a special circumstance."},
            {"q": "Do I earn loyalty points on ticket purchases?",
             "a": "Yes! You earn 1 loyalty point for every €1 spent on tickets. Points are added to your account automatically after payment is confirmed."},
            {"q": "What do the ticket categories (General, VIP, Platinum) include?",
             "a": "General gives standard access. VIP includes priority entry and lounge access. Platinum includes all VIP perks plus meet & greet and premium seating. Full perks are listed on each ticket category page."},
        ],
        "account_faqs": [
            {"q": "How do I change my profile photo?",
             "a": "Click your avatar in the top-right corner to open Account Profile, then upload a new photo. Your Fan Portal photo is set separately under Fan Profile in the sidebar."},
            {"q": "How do I change my password?",
             "a": "Go to Account Profile (top-right avatar) and use the Change Password section, or use Forgot Password on the login page."},
            {"q": "What are loyalty points and membership tiers?",
             "a": "You earn 1 point per €1 spent. Points unlock tiers: Bronze (0 pts), Silver (500 pts), Gold (2,000 pts), Platinum (5,000 pts). Higher tiers unlock exclusive perks and discounts."},
            {"q": "How do I update my email address?",
             "a": "Email changes require identity verification. Contact support@apexforge.com with your request."},
            {"q": "How do I delete my account?",
             "a": "To request account deletion, email support@apexforge.com. All personal data will be removed within 30 days in compliance with GDPR."},
        ],
    }
    return render(request, "fans/help.html", ctx)


@login_required
def fan_profile_edit(request):
    try:
        profile = request.user.fan_profile
    except FanProfile.DoesNotExist:
        profile = FanProfile(user=request.user)
    form = FanProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Profile updated."))
        return redirect("fans:portal")
    return render(request, "fans/profile_form.html", {"form": form})


# ─── Tickets — public browsing ───────────────────────────────────────────────

def ticket_list(request):
    """Browse available tickets grouped by upcoming event."""
    events = (
        Event.objects.filter(
            status="scheduled",
            start_date__gte=timezone.now().date(),
            tickets__status=Ticket.Status.AVAILABLE,
        )
        .distinct()
        .prefetch_related("tickets__category")
        .order_by("start_date")
    )
    return render(request, "fans/ticket_list.html", {"events": events})


def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, status=Ticket.Status.AVAILABLE)
    return render(request, "fans/ticket_detail.html", {"ticket": ticket})


@login_required
def ticket_buy(request, pk):
    """Show ticket detail and redirect to Stripe on POST."""
    import stripe
    from django.conf import settings as dj_settings

    ticket = get_object_or_404(Ticket, pk=pk, status=Ticket.Status.AVAILABLE)
    try:
        fan = request.user.fan_profile
    except FanProfile.DoesNotExist:
        messages.warning(request, _("Please complete your fan profile before buying tickets."))
        return redirect("fans:profile_edit")

    if request.method == "POST":
        # Create pending purchase
        price = ticket.effective_price
        purchase = TicketPurchase.objects.create(
            fan=fan,
            total_amount=price,
            payment_status=TicketPurchase.PaymentStatus.PENDING,
        )
        purchase.tickets.add(ticket)

        # Temporarily reserve the ticket
        ticket.status = Ticket.Status.RESERVED
        ticket.save(update_fields=["status"])

        # Stripe Checkout Session
        stripe.api_key = dj_settings.STRIPE_SECRET_KEY
        base_url = request.build_absolute_uri("/").rstrip("/")

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": dj_settings.STRIPE_CURRENCY,
                        "unit_amount": int(price * 100),
                        "product_data": {
                            "name": f"{_('Ticket')} — {ticket.event.title if ticket.event else ticket.category.name}",
                            "description": ticket.category.name,
                        },
                    },
                    "quantity": 1,
                }],
                mode="payment",
                customer_email=request.user.email,
                metadata={"purchase_id": purchase.pk, "ticket_id": ticket.pk},
                success_url=f"{base_url}/fans/tickets/purchase/{purchase.pk}/success/",
                cancel_url=f"{base_url}/fans/tickets/purchase/{purchase.pk}/cancel/",
            )
            return redirect(session.url, permanent=False)
        except stripe.error.StripeError as e:
            purchase.delete()
            ticket.status = Ticket.Status.AVAILABLE
            ticket.save(update_fields=["status"])
            messages.error(request, _("Payment error: %(err)s") % {"err": str(e)})

    return render(request, "fans/ticket_buy.html", {"ticket": ticket, "fan": fan})


@login_required
@transaction.atomic
def ticket_payment_success(request, purchase_pk):
    """Stripe redirects here after successful ticket payment."""
    purchase = get_object_or_404(TicketPurchase, pk=purchase_pk, fan__user=request.user)
    if purchase.payment_status == TicketPurchase.PaymentStatus.PENDING:
        fan = purchase.fan
        price = purchase.total_amount
        points_earned = int(price)

        # Confirm ticket as sold
        for ticket in purchase.tickets.all():
            ticket.status = Ticket.Status.SOLD
            ticket.owner = fan
            ticket.purchased_at = timezone.now()
            ticket.save(update_fields=["status", "owner", "purchased_at"])

        # Mark purchase paid
        purchase.payment_status = TicketPurchase.PaymentStatus.PAID
        purchase.loyalty_earned = points_earned
        purchase.save(update_fields=["payment_status", "loyalty_earned"])

        # Award loyalty points
        fan.loyalty_points += points_earned
        fan.save(update_fields=["loyalty_points"])
        fan.recalculate_tier()
        LoyaltyTransaction.objects.create(
            fan=fan, points=points_earned,
            tx_type=LoyaltyTransaction.TxType.EARNED,
            description=_("Ticket purchase #%(ref)s") % {"ref": purchase.reference},
        )

    messages.success(
        request,
        _("Ticket confirmed! Reference: %(ref)s. You earned %(pts)s points.")
        % {"ref": purchase.reference, "pts": purchase.loyalty_earned},
    )
    return render(request, "fans/ticket_success.html", {"purchase": purchase})


@login_required
def ticket_payment_cancel(request, purchase_pk):
    """Stripe redirects here when fan cancels ticket payment."""
    purchase = get_object_or_404(TicketPurchase, pk=purchase_pk, fan__user=request.user)
    if purchase.payment_status == TicketPurchase.PaymentStatus.PENDING:
        for ticket in purchase.tickets.all():
            ticket.status = Ticket.Status.AVAILABLE
            ticket.save(update_fields=["status"])
        purchase.payment_status = TicketPurchase.PaymentStatus.FAILED
        purchase.save(update_fields=["payment_status"])
    messages.warning(request, _("Ticket payment was cancelled."))
    return redirect("fans:ticket_list")


@login_required
def my_tickets(request):
    try:
        fan = request.user.fan_profile
    except FanProfile.DoesNotExist:
        return redirect("fans:portal")
    tickets = fan.tickets.select_related("event", "category").order_by("-purchased_at")
    purchases = fan.purchases.prefetch_related("tickets__category", "tickets__event").order_by("-purchased_at")
    return render(request, "fans/my_tickets.html", {
        "fan": fan, "tickets": tickets, "purchases": purchases,
    })


@login_required
def loyalty_history(request):
    try:
        fan = request.user.fan_profile
    except FanProfile.DoesNotExist:
        return redirect("fans:portal")
    transactions = fan.loyalty_transactions.all()
    pts, next_t, pct = fan.tier_progress
    return render(request, "fans/loyalty.html", {
        "fan": fan,
        "transactions": transactions,
        "next_threshold": next_t,
        "tier_pct": pct,
    })


# ─── Admin views (managers only) ─────────────────────────────────────────────

@manager_required
def fan_list(request):
    """Manager view: all registered fan profiles."""
    from django.core.paginator import Paginator
    q = request.GET.get("q", "")
    tier = request.GET.get("tier", "")
    fans = FanProfile.objects.select_related("user").order_by("-created_at")
    if q:
        fans = fans.filter(
            user__first_name__icontains=q
        ) | fans.filter(
            user__last_name__icontains=q
        ) | fans.filter(
            user__email__icontains=q
        )
    if tier:
        fans = fans.filter(tier=tier)
    paginator = Paginator(fans, 25)
    page = paginator.get_page(request.GET.get("page", 1))
    return render(request, "fans/fan_list.html", {
        "page": page,
        "tier_choices": MembershipTier.choices,
        "q": q,
        "current_tier": tier,
    })


@manager_required
def ticket_admin(request):
    """Overview for managers: all tickets, sold count, revenue."""
    categories = TicketCategory.objects.annotate(
        total=Count("tickets"),
        sold=Count("tickets", filter=Q(tickets__status=Ticket.Status.SOLD)),
        revenue=Sum("tickets__price", filter=Q(tickets__status=Ticket.Status.SOLD)),
    )
    recent_purchases = TicketPurchase.objects.select_related("fan__user").order_by("-purchased_at")[:20]
    return render(request, "fans/admin.html", {
        "categories": categories,
        "recent_purchases": recent_purchases,
    })


@manager_required
def ticket_category_list(request):
    categories = TicketCategory.objects.all()
    return render(request, "fans/category_list.html", {"categories": categories})


@manager_required
def ticket_category_create(request):
    form = TicketCategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Category created."))
        return redirect("fans:category_list")
    return render(request, "fans/category_form.html", {"form": form, "title": _("New Category")})


@manager_required
def ticket_category_edit(request, pk):
    cat = get_object_or_404(TicketCategory, pk=pk)
    form = TicketCategoryForm(request.POST or None, instance=cat)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Category updated."))
        return redirect("fans:category_list")
    return render(request, "fans/category_form.html", {"form": form, "title": _("Edit Category")})


@manager_required
def ticket_bulk_create(request):
    """Create many tickets at once for an event."""
    form = TicketBulkCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        event = cd["event"]
        category = cd["category"]
        quantity = cd["quantity"]
        prefix = cd.get("row_prefix", "") or ""
        price = cd.get("price_override")
        tickets = [
            Ticket(
                event=event,
                category=category,
                seat_row=prefix,
                seat_number=str(i + 1),
                price=price,
                status=Ticket.Status.AVAILABLE,
            )
            for i in range(quantity)
        ]
        Ticket.objects.bulk_create(tickets)
        messages.success(request, _("%(n)s tickets created.") % {"n": quantity})
        return redirect("fans:ticket_admin")
    return render(request, "fans/bulk_create.html", {"form": form})


@manager_required
def loyalty_adjust(request):
    form = LoyaltyAdjustForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        fan = cd["fan"]
        pts = cd["points"]
        fan.loyalty_points = max(0, fan.loyalty_points + pts)
        fan.save(update_fields=["loyalty_points"])
        fan.recalculate_tier()
        LoyaltyTransaction.objects.create(
            fan=fan, points=pts,
            tx_type=cd["tx_type"],
            description=cd["description"],
        )
        messages.success(request, _("Loyalty points adjusted for %(name)s.") % {
            "name": fan.user.get_full_name()
        })
        return redirect("fans:ticket_admin")
    return render(request, "fans/loyalty_adjust.html", {"form": form})
