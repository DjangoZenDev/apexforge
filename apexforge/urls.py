"""ApexForge Free Edition — URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("offline/", TemplateView.as_view(template_name="offline.html"), name="offline"),
]
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("core.urls", namespace="core")),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("teams/", include("teams.urls", namespace="teams")),
    path("fans/", include("fans.urls", namespace="fans")),
    path("players/", include("players.urls", namespace="players")),
    path("events/", include("events.urls", namespace="events")),
    path("scouting/", include("scouting.urls", namespace="scouting")),
    path("finance/", include("finance.urls", namespace="finance")),
    path("marketing/", include("marketing.urls", namespace="marketing")),
    path("medical/", include("medical.urls", namespace="medical")),
    path("tournaments/", include("tournaments.urls", namespace="tournaments")),
    path("inventory/", include("inventory.urls", namespace="inventory")),
    path("contracts/", include("contracts.urls", namespace="contracts")),
    path("videos/", include("videos.urls", namespace="videos")),
    path("staff/", include("staff.urls", namespace="staff")),
    path("academy/", include("academy.urls", namespace="academy")),
    path("organizations/", include("organizations.urls", namespace="organizations")),
    path("insights/", include("insights.urls", namespace="insights")),
    prefix_default_language=False,
)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
admin.site.site_header = "ApexForge Admin"
admin.site.site_title = "ApexForge"
admin.site.index_title = "Sports Management Platform"
