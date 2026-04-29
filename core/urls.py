from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("",                        views.landing,               name="landing"),
    path("dashboard/",              views.dashboard,             name="dashboard"),
    path("search/",                 views.search,                name="search"),
    path("activity/",               views.activity_log,          name="activity_log"),
    path("notifications/",          views.notifications_panel,   name="notifications"),
    path("notifications/<int:pk>/read/", views.mark_notification_read, name="notif_read"),
    path("notifications/read-all/", views.mark_all_read,         name="notif_read_all"),
    path("branding/",               views.branding_settings,     name="branding"),
    path("help/",                   views.help_center,           name="help"),
    path("upgrade/",                views.upgrade,               name="upgrade"),
    path("faq/",                    views.public_faq,            name="public_faq"),
    path("terms/",                  views.terms,                 name="terms"),
    path("privacy/",                views.privacy_policy,        name="privacy"),
    path("contact/",                views.contact,               name="contact"),
]
