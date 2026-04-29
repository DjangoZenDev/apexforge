from django.urls import path
from . import views

app_name = "academy"

urlpatterns = [
    path("",                                        views.program_list,     name="programs"),
    path("create/",                                 views.program_create,   name="program_create"),
    path("<int:pk>/",                               views.program_detail,   name="program_detail"),
    path("<int:pk>/edit/",                          views.program_edit,     name="program_edit"),
    path("<int:program_pk>/plan/create/",           views.plan_create,      name="plan_create"),
    path("plan/<int:pk>/",                          views.plan_detail,      name="plan_detail"),
    path("plan/<int:pk>/edit/",                     views.plan_edit,        name="plan_edit"),
    path("plan/<int:plan_pk>/milestone/",           views.milestone_add,    name="milestone_add"),
    path("milestone/<int:pk>/toggle/",              views.milestone_toggle, name="milestone_toggle"),
]
