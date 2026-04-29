from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    # ── Staff finance ─────────────────────────────────────────────────────────
    path("",                                    views.finance_dashboard,         name="dashboard"),
    path("transactions/",                       views.transaction_list,          name="transactions"),
    path("transactions/create/",                views.transaction_create,        name="transaction_create"),
    path("transactions/<int:pk>/edit/",         views.transaction_edit,          name="transaction_edit"),
    path("transactions/export/",                views.export_transactions_excel, name="export_transactions"),
    path("budgets/",                            views.budget_list,               name="budgets"),
    path("budgets/create/",                     views.budget_create,             name="budget_create"),
    path("budgets/<int:pk>/edit/",              views.budget_edit,               name="budget_edit"),
    path("sponsorships/",                       views.sponsorship_list,          name="sponsorships"),
    path("sponsorships/create/",                views.sponsorship_create,        name="sponsorship_create"),
    path("sponsorships/<int:pk>/edit/",         views.sponsorship_edit,          name="sponsorship_edit"),
    path("investments/",                        views.investment_list,           name="investments"),
    path("investments/create/",                 views.investment_create,         name="investment_create"),
    path("investments/<int:pk>/edit/",          views.investment_edit,           name="investment_edit"),

    # ── Store management (staff) ──────────────────────────────────────────────
    path("store/",                              views.product_list,              name="product_list"),
    path("store/add/",                          views.product_create,            name="product_create"),
    path("store/<int:pk>/edit/",                views.product_edit,              name="product_edit"),

    # ── Public shop ───────────────────────────────────────────────────────────
    path("shop/",                               views.shop,                      name="shop"),
    path("shop/<slug:slug>/",                   views.product_detail,            name="product_detail"),

    # ── Cart (works for guests too) ───────────────────────────────────────────
    path("cart/",                               views.cart_view,                 name="cart"),
    path("cart/add/<int:product_id>/",          views.cart_add,                  name="cart_add"),
    path("cart/remove/<int:item_id>/",          views.cart_remove,               name="cart_remove"),

    # ── Checkout & Stripe ─────────────────────────────────────────────────────
    path("checkout/",                           views.checkout,                  name="checkout"),
    path("checkout/submit/",                    views.checkout_submit,           name="checkout_submit"),
    path("orders/<int:pk>/payment/success/",    views.payment_success,           name="payment_success"),
    path("orders/<int:pk>/payment/cancel/",     views.payment_cancel,            name="payment_cancel"),
    path("stripe/webhook/",                     views.stripe_webhook,            name="stripe_webhook"),

    # ── Orders ────────────────────────────────────────────────────────────────
    path("orders/",                             views.order_list,                name="orders"),
    path("orders/<int:pk>/",                    views.order_detail,              name="order_detail"),
    path("orders/<int:pk>/status/",             views.order_status,              name="order_status"),
    path("orders/<int:pk>/invoice/",            views.order_invoice,             name="order_invoice"),
]
