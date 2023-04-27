from django.urls import path
from . import views
from rest_framework import routers

from .views import HIVClinicViewSet

router = routers.DefaultRouter()
router.register(viewset=HIVClinicViewSet, prefix='clinics', basename='clinic')

app_name = 'core'
urlpatterns = [
    path('', views.ApiRootView.as_view(), name='root'),
]
urlpatterns.extend(router.urls)
