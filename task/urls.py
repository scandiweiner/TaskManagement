from django.conf.urls import url
from django.urls import path

from task import views

urlpatterns = [
    path('task/checkin/', views.checkin_view, name='checkin'),
    path('task/checkout/', views.checkout_view, name='checkout'),
    path('task/report/', views.report_view, name="report"),
]
