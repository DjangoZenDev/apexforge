from django.urls import path
from . import views

app_name = "videos"

urlpatterns = [
    path("",                         views.video_library,  name="library"),
    path("upload/",                  views.video_upload,   name="upload"),
    path("<int:pk>/",                views.video_detail,   name="detail"),
    path("<int:pk>/edit/",           views.video_edit,     name="edit"),
    path("<int:video_pk>/note/",     views.add_note,       name="add_note"),
    path("note/<int:pk>/delete/",    views.delete_note,    name="delete_note"),
]
