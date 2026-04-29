from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("",                              views.event_list,        name="list"),
    path("calendar/",                     views.calendar_view,     name="calendar"),
    path("api/",                          views.events_api,        name="api"),
    path("create/",                       views.event_create,      name="create"),
    path("<int:pk>/",                     views.event_detail,      name="detail"),
    path("<int:pk>/edit/",                views.event_edit,        name="edit"),
    path("<int:pk>/delete/",              views.event_delete,      name="delete"),
    path("tournaments/",                  views.tournament_list,   name="tournament_list"),
    path("tournaments/create/",           views.tournament_create, name="tournament_create"),
    path("tournaments/<int:pk>/edit/",    views.tournament_edit,   name="tournament_edit"),
]
