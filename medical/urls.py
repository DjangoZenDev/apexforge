from django.urls import path
from . import views

app_name = "medical"

urlpatterns = [
    path("",                                   views.injury_list,            name="injury_list"),
    path("create/",                            views.injury_create,          name="injury_create"),
    path("create/player/<int:player_pk>/",     views.injury_create,          name="injury_create_for_player"),
    path("<int:pk>/",                          views.injury_detail,          name="injury_detail"),
    path("<int:pk>/edit/",                     views.injury_edit,            name="injury_edit"),
    path("<int:injury_pk>/treatment/",         views.treatment_add,          name="treatment_add"),
    path("<int:injury_pk>/recovery/create/",   views.recovery_plan_create,   name="recovery_create"),
    path("recovery/<int:pk>/edit/",            views.recovery_plan_edit,     name="recovery_edit"),
    path("player/<int:player_pk>/records/",    views.medical_records,        name="records"),
    path("player/<int:player_pk>/records/add/",views.medical_record_create,  name="record_create"),
]
