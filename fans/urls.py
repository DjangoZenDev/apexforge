from django.urls import path
from . import views

app_name = "fans"

urlpatterns = [
    # ── Fan portal ────────────────────────────────────────────────────────────
    path("",                                          views.fan_portal,               name="portal"),
    path("profile/edit/",                             views.fan_profile_edit,         name="profile_edit"),
    path("help/",                                     views.fan_help,                 name="help"),

    # ── Tickets (public browse) ───────────────────────────────────────────────
    path("tickets/",                                  views.ticket_list,              name="ticket_list"),
    path("tickets/<int:pk>/",                         views.ticket_detail,            name="ticket_detail"),
    path("tickets/<int:pk>/buy/",                     views.ticket_buy,               name="ticket_buy"),

    # ── Ticket Stripe payment callbacks ──────────────────────────────────────
    path("tickets/purchase/<int:purchase_pk>/success/", views.ticket_payment_success, name="ticket_payment_success"),
    path("tickets/purchase/<int:purchase_pk>/cancel/",  views.ticket_payment_cancel,  name="ticket_payment_cancel"),

    # ── My tickets & loyalty ─────────────────────────────────────────────────
    path("my-tickets/",                               views.my_tickets,               name="my_tickets"),
    path("loyalty/",                                  views.loyalty_history,          name="loyalty"),

    # ── Admin / manager ───────────────────────────────────────────────────────
    path("admin/fans/",                               views.fan_list,                 name="fan_list"),
    path("admin/",                                    views.ticket_admin,             name="ticket_admin"),
    path("admin/categories/",                         views.ticket_category_list,     name="category_list"),
    path("admin/categories/new/",                     views.ticket_category_create,   name="category_create"),
    path("admin/categories/<int:pk>/edit/",           views.ticket_category_edit,     name="category_edit"),
    path("admin/tickets/bulk/",                       views.ticket_bulk_create,       name="ticket_bulk_create"),
    path("admin/loyalty/adjust/",                     views.loyalty_adjust,           name="loyalty_adjust"),
]
