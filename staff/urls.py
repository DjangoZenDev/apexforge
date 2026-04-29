from django.urls import path
from . import views

app_name = "staff"

urlpatterns = [
    path("",                  views.staff_list,     name="list"),
    path("add/",              views.staff_create,   name="create"),
    path("<int:pk>/",         views.staff_detail,   name="detail"),
    path("<int:pk>/edit/",    views.staff_edit,     name="edit"),
    path("tasks/",            views.task_list,      name="tasks"),
    path("tasks/create/",     views.task_create,    name="task_create"),
    path("tasks/<int:pk>/",   views.task_edit,      name="task_edit"),
    path("payroll/",          views.payroll_list,   name="payroll"),
    path("payroll/create/",          views.payroll_create,    name="payroll_create"),
    path("payroll/<int:pk>/pdf/",    views.payroll_pdf_view,  name="payroll_pdf"),
]
