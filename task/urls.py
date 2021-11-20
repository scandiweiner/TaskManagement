from django.conf.urls import url
from django.urls import path

from task import views

urlpatterns = [
    path('task/checkin/<int:task_id>/', views.checkin_view, name='checkin'),
    path('task/checkout/<int:task_id>/', views.checkout_view, name='checkout'),
    url(r'report/', views.report_view, name="report"),
]
