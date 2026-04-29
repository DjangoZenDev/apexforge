from django.urls import path
from . import views

app_name = "organizations"

urlpatterns = [
    path("",                                      views.org_list,       name="list"),
    path("new/",                                  views.org_create,     name="create"),
    path("<int:pk>/",                             views.org_detail,     name="detail"),
    path("<int:pk>/edit/",                        views.org_edit,       name="edit"),
    # Clubs
    path("<int:org_pk>/clubs/new/",               views.club_create,    name="club_create"),
    path("clubs/<int:pk>/",                       views.club_detail,    name="club_detail"),
    path("clubs/<int:pk>/edit/",                  views.club_edit,      name="club_edit"),
    path("clubs/<int:pk>/switch/",               views.switch_club,    name="switch_club"),
    # Access management
    path("clubs/<int:club_pk>/access/",          views.manage_access,  name="manage_access"),
    path("access/<int:access_pk>/revoke/",       views.revoke_access,  name="revoke_access"),
]
