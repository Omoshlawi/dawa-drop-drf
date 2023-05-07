from django.urls import path, include
from rest_framework import routers

from .views import DoctorsViewSet

app_name = "doctors"
router = routers.DefaultRouter()
router.register(prefix=r'', viewset=DoctorsViewSet, basename='doctor')

urlpatterns = [
    path(r'', include(router.urls)),
]
