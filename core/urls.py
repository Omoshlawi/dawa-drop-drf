from django.urls import path
from . import views
from rest_framework import routers

app_name = 'core'
urlpatterns = [
    path('', views.ApiRootView.as_view(), name='root'),
]
