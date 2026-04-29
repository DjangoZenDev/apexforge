from django.urls import path
from . import views

app_name = "marketing"

urlpatterns = [
    path("news/",                          views.news_list,            name="news_list"),
    path("news/create/",                   views.news_create,          name="news_create"),
    path("news/<slug:slug>/",              views.news_detail,          name="news_detail"),
    path("news/<slug:slug>/edit/",         views.news_edit,            name="news_edit"),
    path("news/<slug:slug>/delete/",       views.news_delete,          name="news_delete"),
    path("announcements/",                 views.announcements,        name="announcements"),
    path("announcements/<int:pk>/edit/",   views.announcement_edit,    name="announcement_edit"),
    path("announcements/<int:pk>/delete/", views.announcement_delete,  name="announcement_delete"),
    path("campaigns/",                     views.campaigns,            name="campaigns"),
    path("campaigns/",                     views.campaigns,            name="campaign_list"),
    path("campaigns/create/",              views.campaign_create,      name="campaign_create"),
    path("campaigns/<int:pk>/",            views.campaign_detail,      name="campaign_detail"),
    path("campaigns/<int:pk>/edit/",       views.campaign_edit,        name="campaign_edit"),
    path("sponsors/",                      views.sponsor_portal,       name="sponsor_portal"),
]
