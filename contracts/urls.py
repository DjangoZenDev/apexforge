from django.urls import path
from . import views

app_name = "contracts"

urlpatterns = [
    path("",                          views.contract_list,    name="list"),
    path("create/",                   views.contract_create,  name="create"),
    path("<int:pk>/",                 views.contract_detail,  name="detail"),
    path("<int:pk>/edit/",            views.contract_edit,    name="edit"),
    path("<int:contract_pk>/clause/", views.clause_add,       name="clause_add"),
    path("<int:pk>/sign/",            views.sign_contract,    name="sign"),
    path("<int:pk>/pdf/",             views.contract_pdf_view, name="pdf"),
]
