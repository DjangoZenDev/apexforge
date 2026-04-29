from django.urls import path
from . import views

app_name = "scouting"

urlpatterns = [
    path("",                              views.scouting_dashboard,       name="dashboard"),
    path("talents/",                      views.talent_list,              name="talent_list"),
    path("talents/create/",               views.talent_create,            name="talent_create"),
    path("talents/<int:pk>/",             views.talent_detail,            name="talent_detail"),
    path("talents/<int:pk>/edit/",        views.talent_edit,              name="talent_edit"),
    path("reports/",                      views.report_list,              name="report_list"),
    path("reports/create/",               views.report_create,            name="report_create"),
    path("reports/<int:pk>/",             views.report_detail,            name="report_detail"),
    path("reports/<int:pk>/edit/",        views.report_edit,              name="report_edit"),
    path("watchlist/",                    views.watchlist_view,           name="watchlist"),
    path("watchlist/<int:wl_pk>/add/<int:player_pk>/",
         views.watchlist_add_player,      name="watchlist_add_player"),
    path("watchlist/remove-player/<int:pk>/",
         views.watchlist_remove_player,   name="watchlist_remove_player"),
    path("watchlist/remove-talent/<int:pk>/",
         views.watchlist_remove_talent,   name="watchlist_remove_talent"),
]
