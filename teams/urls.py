from django.urls import path
from . import views

app_name = "teams"

urlpatterns = [
    path("",                            views.team_list,         name="list"),
    path("create/",                     views.team_create,       name="create"),
    path("<int:pk>/",                   views.team_detail,       name="detail"),
    path("<int:pk>/edit/",              views.team_edit,         name="edit"),
    path("<int:pk>/delete/",            views.team_delete,       name="delete"),
    path("<int:team_pk>/roster/add/",   views.roster_add,        name="roster_add"),
    path("<int:pk>/roster/export/",          views.export_roster_csv,  name="export_roster"),
    path("<int:pk>/roster/import/",          views.import_roster_csv,  name="import_roster"),
    path("<int:team_pk>/roster/demo/",        views.generate_demo_squad, name="roster_demo"),
    path("seasons/",                         views.season_list,        name="seasons"),
    path("seasons/<int:pk>/set-current/",    views.season_set_current, name="season_set_current"),
    path("seasons/<int:pk>/delete/",         views.season_delete,      name="season_delete"),
]
