from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("",                           views.inventory_list,   name="list"),
    path("add/",                       views.item_create,      name="create"),
    path("<int:pk>/",                  views.item_detail,      name="item_detail"),
    path("<int:pk>/edit/",             views.item_edit,        name="edit"),
    path("<int:item_pk>/movement/",    views.stock_movement,   name="movement"),
    path("<int:item_pk>/assign/",      views.kit_assign,       name="assign"),
    path("assignment/<int:pk>/return/",views.kit_return,       name="return"),
]
