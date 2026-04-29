from django.urls import path
from . import views

app_name = "players"

urlpatterns = [
    path("",                         views.player_list,    name="list"),
    path("create/",                  views.player_create,  name="create"),
    path("export/",                  views.export_players_excel, name="export"),
    path("<int:pk>/",                views.player_detail,  name="detail"),
    path("<int:pk>/edit/",           views.player_edit,    name="edit"),
    path("<int:pk>/delete/",         views.player_delete,  name="delete"),
    path("<int:pk>/stats/add/",      views.add_stats,      name="add_stats"),
    path("<int:pk>/injury/add/",     views.add_injury,     name="add_injury"),
    path("<int:pk>/metric/add/",     views.add_metric,     name="add_metric"),
    path("<int:pk>/pdf/",            views.player_pdf,     name="pdf"),
]
