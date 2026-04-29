from django.urls import path
from . import views

app_name = "tournaments"

urlpatterns = [
    path("",                              views.competition_list,    name="list"),
    path("create/",                       views.competition_create,  name="create"),
    path("<slug:slug>/",                  views.competition_detail,  name="detail"),
    path("<slug:slug>/edit/",             views.competition_edit,    name="edit"),
    path("<slug:competition_slug>/match/create/", views.match_create, name="match_create"),
    path("match/<int:pk>/edit/",          views.match_edit,          name="match_edit"),
    path("match/<int:pk>/lineup/",        views.lineup_builder,      name="lineup"),
    path("match/<int:pk>/lineup/save/",   views.lineup_save,         name="lineup_save"),
    path("<slug:slug>/standings/",        views.standings_view,      name="standings"),
]
